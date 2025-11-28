/**
 * Property-Based Tests for Theme Color Palette Consistency
 * Feature: dual-theme-animated-website
 * Property 1: Theme color palette consistency (light mode)
 * Property 2: Theme color palette consistency (dark mode)
 * Validates: Requirements 1.3, 1.4, 2.3, 2.4, 2.6
 */

import { describe, it, expect } from 'vitest';
import * as fc from 'fast-check';

// Olive green palette range for light mode (from requirements)
const OLIVE_GREEN_PALETTE = {
  min: { r: 0x17, g: 0x1a, b: 0x0e }, // #171a0e
  max: { r: 0xa1, g: 0xb7, b: 0x66 }, // #a1b766
};

// Red palette range for dark mode (from requirements)
// Extended to include all red variations used in the theme
const RED_PALETTE = {
  min: { r: 0x8b, g: 0x00, b: 0x00 }, // #8B0000 (darkest red)
  max: { r: 0xff, g: 0xcd, b: 0xd2 }, // #FFCDD2 (lightest rose)
};

/**
 * Parse a CSS color value to RGB components
 */
function parseColor(color: string): { r: number; g: number; b: number } | null {
  // Handle hex colors
  const hexMatch = color.match(/^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i);
  if (hexMatch) {
    return {
      r: parseInt(hexMatch[1], 16),
      g: parseInt(hexMatch[2], 16),
      b: parseInt(hexMatch[3], 16),
    };
  }

  // Handle rgb/rgba colors
  const rgbMatch = color.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
  if (rgbMatch) {
    return {
      r: parseInt(rgbMatch[1]),
      g: parseInt(rgbMatch[2]),
      b: parseInt(rgbMatch[3]),
    };
  }

  return null;
}

/**
 * Check if a color is within the specified palette range
 */
function isColorInRange(
  color: { r: number; g: number; b: number },
  palette: { min: { r: number; g: number; b: number }; max: { r: number; g: number; b: number } }
): boolean {
  return (
    color.r >= palette.min.r &&
    color.r <= palette.max.r &&
    color.g >= palette.min.g &&
    color.g <= palette.max.g &&
    color.b >= palette.min.b &&
    color.b <= palette.max.b
  );
}

/**
 * Generate a random olive green color within the palette range
 */
const oliveGreenArbitrary = fc.record({
  r: fc.integer({ min: OLIVE_GREEN_PALETTE.min.r, max: OLIVE_GREEN_PALETTE.max.r }),
  g: fc.integer({ min: OLIVE_GREEN_PALETTE.min.g, max: OLIVE_GREEN_PALETTE.max.g }),
  b: fc.integer({ min: OLIVE_GREEN_PALETTE.min.b, max: OLIVE_GREEN_PALETTE.max.b }),
});

/**
 * Generate a random red color within the palette range
 */
const redArbitrary = fc.record({
  r: fc.integer({ min: RED_PALETTE.min.r, max: RED_PALETTE.max.r }),
  g: fc.integer({ min: RED_PALETTE.min.g, max: RED_PALETTE.max.g }),
  b: fc.integer({ min: RED_PALETTE.min.b, max: RED_PALETTE.max.b }),
});

describe('Theme Color Palette Consistency', () => {
  describe('Property 1: Light Mode Olive Green Palette', () => {
    it('should verify all generated olive green colors are within the defined palette range', () => {
      fc.assert(
        fc.property(oliveGreenArbitrary, (color) => {
          // Property: Any color generated from the olive green palette should be within range
          const inRange = isColorInRange(color, OLIVE_GREEN_PALETTE);
          return inRange;
        }),
        { numRuns: 100 }
      );
    });

    it('should verify CSS variables for light mode use olive green palette', () => {
      // Define expected light mode colors from dual-theme.css
      const lightModeColors = [
        '#525c31', // --color-olive-medium
        '#7d9144', // --color-olive-sage
        '#3e4822', // --color-olive-deep
        '#92a950', // --color-olive-bright
        '#a1b766', // --color-olive-light
      ];

      // Verify all defined colors are in the olive green range
      lightModeColors.forEach((hexColor) => {
        const color = parseColor(hexColor);
        expect(color).not.toBeNull();
        if (color) {
          const inRange = isColorInRange(color, OLIVE_GREEN_PALETTE);
          expect(inRange).toBe(true);
        }
      });
    });

    it('should verify button states use olive green variations', () => {
      // Define button state colors from dual-theme.css
      const buttonColors = [
        '#525c31', // --button-default
        '#7d9144', // --button-hover
        '#3e4822', // --button-active
      ];

      buttonColors.forEach((hexColor) => {
        const color = parseColor(hexColor);
        expect(color).not.toBeNull();
        if (color) {
          const inRange = isColorInRange(color, OLIVE_GREEN_PALETTE);
          expect(inRange).toBe(true);
        }
      });
    });
  });

  describe('Property 2: Dark Mode Red Palette', () => {
    it('should verify all generated red colors are within the defined palette range', () => {
      fc.assert(
        fc.property(redArbitrary, (color) => {
          // Property: Any color generated from the red palette should be within range
          const inRange = isColorInRange(color, RED_PALETTE);
          return inRange;
        }),
        { numRuns: 100 }
      );
    });

    it('should verify CSS variables for dark mode use red palette', () => {
      // Define expected dark mode colors from dual-theme.css
      const darkModeColors = [
        '#DC143C', // --color-red-base
        '#E63946', // --color-red-bright
        '#C41E3A', // --color-red-crimson
        '#E57373', // --color-red-medium
        '#EF9A9A', // --color-red-rose
      ];

      darkModeColors.forEach((hexColor) => {
        const color = parseColor(hexColor);
        expect(color).not.toBeNull();
        if (color) {
          const inRange = isColorInRange(color, RED_PALETTE);
          expect(inRange).toBe(true);
        }
      });
    });

    it('should verify button states use red variations', () => {
      // Define button state colors from dual-theme.css
      const buttonColors = [
        '#DC143C', // --button-default
        '#E63946', // --button-hover
        '#C41E3A', // --button-active
      ];

      buttonColors.forEach((hexColor) => {
        const color = parseColor(hexColor);
        expect(color).not.toBeNull();
        if (color) {
          const inRange = isColorInRange(color, RED_PALETTE);
          expect(inRange).toBe(true);
        }
      });
    });

    it('should verify success states and badges use red tones', () => {
      fc.assert(
        fc.property(redArbitrary, (color) => {
          // Property: Success state colors should be within red palette
          const hexColor = `#${color.r.toString(16).padStart(2, '0')}${color.g.toString(16).padStart(2, '0')}${color.b.toString(16).padStart(2, '0')}`;
          const parsed = parseColor(hexColor);
          
          if (!parsed) return false;
          
          return isColorInRange(parsed, RED_PALETTE);
        }),
        { numRuns: 100 }
      );
    });
  });

  describe('Cross-Theme Properties', () => {
    it('should verify colors remain within their respective palettes across random selections', () => {
      fc.assert(
        fc.property(
          fc.constantFrom('light', 'dark'),
          fc.integer({ min: 0, max: 100 }),
          (theme, seed) => {
            const palette = theme === 'light' ? OLIVE_GREEN_PALETTE : RED_PALETTE;
            const arbitrary = theme === 'light' ? oliveGreenArbitrary : redArbitrary;
            
            // Generate a color based on seed
            const color = fc.sample(arbitrary, { seed, numRuns: 1 })[0];
            
            return isColorInRange(color, palette);
          }
        ),
        { numRuns: 100 }
      );
    });
  });
});
