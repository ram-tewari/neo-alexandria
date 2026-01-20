"""
Final chunking verification with longer content.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.shared.database import init_database
from app.config.settings import get_settings

settings = get_settings()
init_database(settings.get_database_url(), settings.ENV)

from app.shared.database import SessionLocal
from app.modules.resources.service import create_pending_resource, ChunkingService

def test_chunking_with_long_content():
    """Test chunking with artificially long content."""
    print("=" * 60)
    print("FINAL CHUNKING VERIFICATION")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Create long content (multiple paragraphs)
        long_content = """
        Artificial Intelligence and Machine Learning have revolutionized the way we approach problem-solving in computer science. 
        These technologies enable systems to learn from data and improve their performance over time without being explicitly programmed.
        
        Deep learning, a subset of machine learning, uses neural networks with multiple layers to progressively extract higher-level 
        features from raw input. For example, in image processing, lower layers may identify edges, while higher layers may identify 
        concepts relevant to a human such as digits or letters or faces.
        
        Natural Language Processing (NLP) is another crucial area where AI has made significant strides. NLP enables computers to 
        understand, interpret, and generate human language in a valuable way. Applications include machine translation, sentiment 
        analysis, chatbots, and text summarization.
        
        Computer Vision allows machines to derive meaningful information from digital images, videos, and other visual inputs. 
        This technology powers applications like facial recognition, autonomous vehicles, medical image analysis, and augmented reality.
        
        Reinforcement Learning is a type of machine learning where an agent learns to make decisions by performing actions in an 
        environment to maximize cumulative reward. This approach has been successfully applied to game playing, robotics, and 
        resource management.
        
        The ethical implications of AI are increasingly important as these systems become more prevalent in society. Issues include 
        bias in algorithms, privacy concerns, job displacement, and the need for transparency and accountability in AI decision-making.
        
        Cloud computing has become essential for AI development, providing the computational resources needed to train large models. 
        Major cloud providers offer specialized AI services and infrastructure that democratize access to advanced AI capabilities.
        
        The future of AI promises even more exciting developments, including artificial general intelligence (AGI), quantum machine 
        learning, and AI systems that can explain their reasoning processes. These advances will continue to transform industries 
        and create new opportunities for innovation.
        """ * 3  # Repeat 3 times to ensure multiple chunks
        
        print(f"\n📝 Test content length: {len(long_content)} characters")
        print(f"   Words (approx): {len(long_content.split())}")
        
        # Get chunking settings
        print(f"\n⚙️  Chunking Configuration:")
        print(f"   Strategy: {settings.CHUNKING_STRATEGY}")
        print(f"   Chunk Size: {settings.CHUNK_SIZE} words")
        print(f"   Overlap: {settings.CHUNK_OVERLAP} words")
        
        # Create chunking service
        chunking_service = ChunkingService(
            db=db,
            strategy=settings.CHUNKING_STRATEGY,
            chunk_size=settings.CHUNK_SIZE,
            overlap=settings.CHUNK_OVERLAP,
        )
        
        # Test semantic chunking
        print(f"\n🔧 Testing semantic chunking...")
        chunks = chunking_service.semantic_chunk(
            resource_id="test-resource-id",
            content=long_content,
            chunk_metadata={"test": True}
        )
        
        print(f"\n📦 Chunks created: {len(chunks)}")
        for i, chunk in enumerate(chunks[:5]):  # Show first 5
            content_preview = chunk['content'][:100].replace('\n', ' ')
            print(f"   Chunk {i}: {len(chunk['content'])} chars - {content_preview}...")
        
        if len(chunks) > 5:
            print(f"   ... and {len(chunks) - 5} more chunks")
        
        print("\n" + "=" * 60)
        if len(chunks) > 1:
            print(f"✅ SUCCESS: Multiple chunks created ({len(chunks)} chunks)")
            print("\nChunking is working correctly!")
            print("The issue with the Postman URL was that the extracted")
            print("text was too short (~200 words), which fits in 1 chunk.")
        else:
            print(f"⚠️  Only {len(chunks)} chunk created")
            print("Content might still be too short for multiple chunks")
        print("=" * 60)
        
        return len(chunks) > 1
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = test_chunking_with_long_content()
    sys.exit(0 if success else 1)
