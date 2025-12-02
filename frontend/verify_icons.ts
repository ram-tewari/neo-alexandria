import { icons } from './src/config/icons';

console.log('Verifying icons...');
const undefinedIcons: string[] = [];

for (const [key, value] of Object.entries(icons)) {
    if (value === undefined) {
        console.error(`Icon '${key}' is undefined!`);
        undefinedIcons.push(key);
    }
}

if (undefinedIcons.length === 0) {
    console.log('All icons are defined.');
} else {
    console.error(`Found ${undefinedIcons.length} undefined icons.`);
    process.exit(1);
}
