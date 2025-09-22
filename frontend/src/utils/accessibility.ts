/**
 * Accessibility Utilities
 * 
 * Utility functions and constants for improving web accessibility.
 */

/**
 * ARIA roles for common UI elements
 */
export const ARIA_ROLES = {
  BUTTON: 'button',
  LINK: 'link',
  MENU: 'menu',
  MENUITEM: 'menuitem',
  DIALOG: 'dialog',
  ALERT: 'alert',
  STATUS: 'status',
  TAB: 'tab',
  TABLIST: 'tablist',
  TABPANEL: 'tabpanel',
  NAVIGATION: 'navigation',
  MAIN: 'main',
  BANNER: 'banner',
  CONTENTINFO: 'contentinfo',
  COMPLEMENTARY: 'complementary',
  SEARCH: 'search',
  FORM: 'form',
  GROUP: 'group',
  RADIOGROUP: 'radiogroup',
  CHECKBOX: 'checkbox',
  TEXTBOX: 'textbox',
  COMBOBOX: 'combobox',
  LISTBOX: 'listbox',
  OPTION: 'option',
  PROGRESSBAR: 'progressbar',
  SLIDER: 'slider',
  SPINBUTTON: 'spinbutton',
  SWITCH: 'switch',
  TREE: 'tree',
  TREEITEM: 'treeitem',
} as const;

/**
 * ARIA properties for common attributes
 */
export const ARIA_PROPERTIES = {
  EXPANDED: 'aria-expanded',
  SELECTED: 'aria-selected',
  CHECKED: 'aria-checked',
  PRESSED: 'aria-pressed',
  DISABLED: 'aria-disabled',
  HIDDEN: 'aria-hidden',
  LABEL: 'aria-label',
  LABELLEDBY: 'aria-labelledby',
  DESCRIBEDBY: 'aria-describedby',
  REQUIRED: 'aria-required',
  INVALID: 'aria-invalid',
  LIVE: 'aria-live',
  ATOMIC: 'aria-atomic',
  RELEVANT: 'aria-relevant',
  ORIENTATION: 'aria-orientation',
  LEVEL: 'aria-level',
  POSINSET: 'aria-posinset',
  SETSIZE: 'aria-setsize',
  SORT: 'aria-sort',
  VALUENOW: 'aria-valuenow',
  VALUEMIN: 'aria-valuemin',
  VALUEMAX: 'aria-valuemax',
  VALUETEXT: 'aria-valuetext',
  CONTROLS: 'aria-controls',
  OWNS: 'aria-owns',
  FLOWTO: 'aria-flowto',
  ACTIVE: 'aria-activedescendant',
  MULTISELECTABLE: 'aria-multiselectable',
  READONLY: 'aria-readonly',
  MODAL: 'aria-modal',
  AUTOPLACE: 'aria-autocomplete',
} as const;

/**
 * Common ARIA live regions
 */
export const ARIA_LIVE_REGIONS = {
  POLITE: 'polite',
  ASSERTIVE: 'assertive',
  OFF: 'off',
} as const;

/**
 * Keyboard navigation key codes
 */
export const KEYBOARD_KEYS = {
  ENTER: 'Enter',
  SPACE: ' ',
  ESCAPE: 'Escape',
  TAB: 'Tab',
  ARROW_UP: 'ArrowUp',
  ARROW_DOWN: 'ArrowDown',
  ARROW_LEFT: 'ArrowLeft',
  ARROW_RIGHT: 'ArrowRight',
  HOME: 'Home',
  END: 'End',
  PAGE_UP: 'PageUp',
  PAGE_DOWN: 'PageDown',
  DELETE: 'Delete',
  BACKSPACE: 'Backspace',
} as const;

/**
 * Focus management utilities
 */
export class FocusManager {
  /**
   * Trap focus within a container element
   */
  static trapFocus(container: HTMLElement): () => void {
    const focusableElements = FocusManager.getFocusableElements(container);
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === KEYBOARD_KEYS.TAB) {
        if (event.shiftKey) {
          // Shift + Tab
          if (document.activeElement === firstElement) {
            event.preventDefault();
            lastElement?.focus();
          }
        } else {
          // Tab
          if (document.activeElement === lastElement) {
            event.preventDefault();
            firstElement?.focus();
          }
        }
      }
    };

    container.addEventListener('keydown', handleKeyDown);
    
    // Focus the first element
    firstElement?.focus();

    // Return cleanup function
    return () => {
      container.removeEventListener('keydown', handleKeyDown);
    };
  }

  /**
   * Get all focusable elements within a container
   */
  static getFocusableElements(container: HTMLElement): HTMLElement[] {
    const focusableSelectors = [
      'button:not([disabled])',
      'input:not([disabled])',
      'select:not([disabled])',
      'textarea:not([disabled])',
      'a[href]',
      '[tabindex]:not([tabindex="-1"])',
      '[contenteditable="true"]',
    ].join(', ');

    return Array.from(container.querySelectorAll(focusableSelectors)) as HTMLElement[];
  }

  /**
   * Restore focus to a previously focused element
   */
  static restoreFocus(previousElement: HTMLElement | null): void {
    if (previousElement && typeof previousElement.focus === 'function') {
      previousElement.focus();
    }
  }

  /**
   * Get the currently focused element
   */
  static getCurrentFocus(): HTMLElement | null {
    return document.activeElement as HTMLElement;
  }
}

/**
 * Screen reader utilities
 */
export class ScreenReader {
  /**
   * Announce a message to screen readers
   */
  static announce(message: string, priority: 'polite' | 'assertive' = 'polite'): void {
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', priority);
    announcement.setAttribute('aria-atomic', 'true');
    announcement.className = 'sr-only';
    announcement.textContent = message;

    document.body.appendChild(announcement);

    // Remove the announcement after a short delay
    setTimeout(() => {
      document.body.removeChild(announcement);
    }, 1000);
  }

  /**
   * Create a visually hidden element for screen readers
   */
  static createVisuallyHidden(text: string): HTMLElement {
    const element = document.createElement('span');
    element.className = 'sr-only';
    element.textContent = text;
    return element;
  }
}

/**
 * Form accessibility utilities
 */
export class FormAccessibility {
  /**
   * Generate a unique ID for form elements
   */
  static generateId(prefix: string = 'form'): string {
    return `${prefix}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Associate a label with a form control
   */
  static associateLabel(control: HTMLElement, labelText: string): HTMLElement {
    const labelId = FormAccessibility.generateId('label');
    const controlId = FormAccessibility.generateId('control');

    control.id = controlId;
    control.setAttribute('aria-labelledby', labelId);

    const label = document.createElement('label');
    label.id = labelId;
    label.htmlFor = controlId;
    label.textContent = labelText;

    return label;
  }

  /**
   * Add error message association to a form control
   */
  static associateErrorMessage(control: HTMLElement, errorMessage: string): HTMLElement {
    const errorId = FormAccessibility.generateId('error');
    const describedBy = control.getAttribute('aria-describedby') || '';
    const newDescribedBy = describedBy ? `${describedBy} ${errorId}` : errorId;

    control.setAttribute('aria-describedby', newDescribedBy);
    control.setAttribute('aria-invalid', 'true');

    const errorElement = document.createElement('div');
    errorElement.id = errorId;
    errorElement.className = 'error-message';
    errorElement.setAttribute('role', 'alert');
    errorElement.textContent = errorMessage;

    return errorElement;
  }

  /**
   * Remove error message association from a form control
   */
  static removeErrorMessage(control: HTMLElement, errorId: string): void {
    const describedBy = control.getAttribute('aria-describedby') || '';
    const newDescribedBy = describedBy
      .split(' ')
      .filter(id => id !== errorId)
      .join(' ');

    if (newDescribedBy) {
      control.setAttribute('aria-describedby', newDescribedBy);
    } else {
      control.removeAttribute('aria-describedby');
    }

    control.removeAttribute('aria-invalid');
  }
}

/**
 * Navigation accessibility utilities
 */
export class NavigationAccessibility {
  /**
   * Handle keyboard navigation for menu items
   */
  static handleMenuNavigation(
    event: KeyboardEvent,
    items: HTMLElement[],
    currentIndex: number
  ): number {
    switch (event.key) {
      case KEYBOARD_KEYS.ARROW_DOWN:
        event.preventDefault();
        return (currentIndex + 1) % items.length;
      
      case KEYBOARD_KEYS.ARROW_UP:
        event.preventDefault();
        return currentIndex === 0 ? items.length - 1 : currentIndex - 1;
      
      case KEYBOARD_KEYS.HOME:
        event.preventDefault();
        return 0;
      
      case KEYBOARD_KEYS.END:
        event.preventDefault();
        return items.length - 1;
      
      case KEYBOARD_KEYS.ESCAPE:
        event.preventDefault();
        return -1; // Signal to close menu
      
      default:
        return currentIndex;
    }
  }

  /**
   * Handle keyboard navigation for tab panels
   */
  static handleTabNavigation(
    event: KeyboardEvent,
    tabs: HTMLElement[],
    currentIndex: number
  ): number {
    switch (event.key) {
      case KEYBOARD_KEYS.ARROW_LEFT:
        event.preventDefault();
        return currentIndex === 0 ? tabs.length - 1 : currentIndex - 1;
      
      case KEYBOARD_KEYS.ARROW_RIGHT:
        event.preventDefault();
        return (currentIndex + 1) % tabs.length;
      
      case KEYBOARD_KEYS.HOME:
        event.preventDefault();
        return 0;
      
      case KEYBOARD_KEYS.END:
        event.preventDefault();
        return tabs.length - 1;
      
      default:
        return currentIndex;
    }
  }
}

/**
 * Color contrast utilities
 */
export class ColorContrast {
  /**
   * Calculate the relative luminance of a color
   */
  static getRelativeLuminance(r: number, g: number, b: number): number {
    const [rs, gs, bs] = [r, g, b].map(c => {
      c = c / 255;
      return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    });
    
    return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
  }

  /**
   * Calculate the contrast ratio between two colors
   */
  static getContrastRatio(color1: [number, number, number], color2: [number, number, number]): number {
    const l1 = ColorContrast.getRelativeLuminance(...color1);
    const l2 = ColorContrast.getRelativeLuminance(...color2);
    
    const lighter = Math.max(l1, l2);
    const darker = Math.min(l1, l2);
    
    return (lighter + 0.05) / (darker + 0.05);
  }

  /**
   * Check if contrast ratio meets WCAG standards
   */
  static meetsWCAG(color1: [number, number, number], color2: [number, number, number], level: 'AA' | 'AAA' = 'AA'): boolean {
    const ratio = ColorContrast.getContrastRatio(color1, color2);
    return level === 'AA' ? ratio >= 4.5 : ratio >= 7;
  }
}

/**
 * Accessibility testing utilities
 */
export class AccessibilityTester {
  /**
   * Check if an element has proper ARIA labels
   */
  static hasAriaLabel(element: HTMLElement): boolean {
    return !!(
      element.getAttribute('aria-label') ||
      element.getAttribute('aria-labelledby') ||
      element.getAttribute('title') ||
      (element.tagName === 'INPUT' && element.getAttribute('placeholder'))
    );
  }

  /**
   * Check if an element is keyboard accessible
   */
  static isKeyboardAccessible(element: HTMLElement): boolean {
    const tagName = element.tagName.toLowerCase();
    const tabIndex = element.getAttribute('tabindex');
    
    // Elements that are naturally keyboard accessible
    if (['a', 'button', 'input', 'select', 'textarea'].includes(tagName)) {
      return !element.hasAttribute('disabled');
    }
    
    // Elements with tabindex >= 0
    if (tabIndex && parseInt(tabIndex) >= 0) {
      return true;
    }
    
    return false;
  }

  /**
   * Check if an element has proper focus indicators
   */
  static hasFocusIndicator(element: HTMLElement): boolean {
    const styles = window.getComputedStyle(element, ':focus');
    return !!(
      styles.outline !== 'none' ||
      styles.boxShadow !== 'none' ||
      styles.borderColor !== styles.borderColor
    );
  }
}
