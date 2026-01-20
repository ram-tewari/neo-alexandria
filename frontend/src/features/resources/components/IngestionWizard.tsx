import { useState } from 'react';
import { useForm } from 'react-hook-form';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger
} from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { toast } from 'sonner';
import { Plus, Loader2 } from 'lucide-react';
import { useIngestResource } from '../hooks/useIngestResource';

interface IngestionWizardProps {
  trigger?: React.ReactNode;
}

interface IngestionFormData {
  url: string;
  title?: string;
}

export function IngestionWizard({ trigger }: IngestionWizardProps) {
  const [open, setOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('url');
  const { mutate: ingest, isPending } = useIngestResource();

  const { register, handleSubmit, reset, formState: { errors } } = useForm<IngestionFormData>();

  const onSubmit = (data: IngestionFormData) => {
    ingest(
      { url: data.url, title: data.title },
      {
        onSuccess: () => {
          toast.success('Ingestion Started', {
            description: 'Your resource is being processed.'
          });
          setOpen(false);
          reset();
        },
        onError: (error: any) => {
          console.error('Ingestion error:', error);
          
          // Handle network errors
          if (!error.response) {
            toast.error('Network Error', {
              description: 'Network error. Please check your connection.'
            });
            return;
          }

          // Handle rate limiting
          if (error.response.status === 429) {
            const retryAfter = error.response.headers['retry-after'] || '60';
            toast.error('Rate Limit Exceeded', {
              description: `Rate limit exceeded. Please try again in ${retryAfter} seconds.`
            });
            return;
          }

          // Handle server errors
          if (error.response.status >= 500) {
            toast.error('Server Error', {
              description: 'Server error. Please try again later.'
            });
            return;
          }

          // Handle validation errors (400)
          const errorMessage = error.response?.data?.detail || 'An error occurred';
          toast.error('Ingestion Failed', {
            description: errorMessage
          });
        }
      }
    );
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || (
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Add Resource
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[525px]">
        <DialogHeader>
          <DialogTitle>Add Resource</DialogTitle>
          <DialogDescription>
            Choose a method to add resources to your library.
          </DialogDescription>
        </DialogHeader>

        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="url">Single URL</TabsTrigger>
            <TabsTrigger value="file" disabled>File Upload</TabsTrigger>
            <TabsTrigger value="batch" disabled>Batch Paste</TabsTrigger>
          </TabsList>

          <TabsContent value="url" className="space-y-4">
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div>
                <Label htmlFor="url">Resource URL</Label>
                <Input
                  id="url"
                  type="url"
                  placeholder="https://example.com/article"
                  {...register('url', { 
                    required: 'URL is required',
                    pattern: {
                      value: /^https?:\/\/.+/,
                      message: 'URL must start with http:// or https://'
                    }
                  })}
                />
                {errors.url && (
                  <p className="text-sm text-destructive mt-1">
                    {errors.url.message}
                  </p>
                )}
              </div>
              <div>
                <Label htmlFor="title">Title (Optional)</Label>
                <Input
                  id="title"
                  placeholder="Custom title for this resource"
                  {...register('title')}
                />
              </div>
              <Button type="submit" disabled={isPending} className="w-full">
                {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Ingest
              </Button>
            </form>
          </TabsContent>

          <TabsContent value="file" className="space-y-4">
            <div>
              <Label htmlFor="file">Upload File</Label>
              <Input
                id="file"
                type="file"
                accept=".pdf,.txt"
                disabled
              />
              <p className="text-sm text-muted-foreground mt-2">
                File upload coming soon. Currently supports PDF and TXT files.
              </p>
            </div>
          </TabsContent>

          <TabsContent value="batch" className="space-y-4">
            <div>
              <Label htmlFor="batch">URLs (one per line)</Label>
              <Textarea
                id="batch"
                placeholder="https://example.com/article1&#10;https://example.com/article2"
                rows={6}
                disabled
              />
              <p className="text-sm text-muted-foreground mt-2">
                Batch ingestion coming soon.
              </p>
            </div>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
