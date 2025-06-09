/**
 * Utility functions for parsing full names into first and last names
 * and creating full names from first and last names
 */

export interface ParsedName {
  first_name: string;
  last_name: string;
}

/**
 * Create a full name from first and last names
 * 
 * Examples:
 * - ("John", "Doe") -> "John Doe"
 * - ("Mark Anthony", "Navarro") -> "Mark Anthony Navarro"
 * - ("Madonna", "") -> "Madonna"
 * - ("", "Doe") -> "Doe"
 * - ("", "") -> ""
 */
export function createFullName(firstName: string, lastName: string): string {
  const trimmedFirst = (firstName || '').trim();
  const trimmedLast = (lastName || '').trim();
  
  if (!trimmedFirst && !trimmedLast) {
    return '';
  }
  
  if (!trimmedFirst) {
    return trimmedLast;
  }
  
  if (!trimmedLast) {
    return trimmedFirst;
  }
  
  return `${trimmedFirst} ${trimmedLast}`;
}

/**
 * Parse a full name into first and last name components
 * This function assumes the last word is the last name, and everything before it is the first name
 * 
 * Examples:
 * - "Mark Anthony Navarro" -> { first_name: "Mark Anthony", last_name: "Navarro" }
 * - "John Doe" -> { first_name: "John", last_name: "Doe" }
 * - "Madonna" -> { first_name: "Madonna", last_name: "" }
 * - "Jean-Claude Van Damme" -> { first_name: "Jean-Claude Van", last_name: "Damme" }
 */
export function parseFullName(fullName: string): ParsedName {
  if (!fullName || typeof fullName !== 'string') {
    return { first_name: '', last_name: '' };
  }

  const trimmedName = fullName.trim();
  if (!trimmedName) {
    return { first_name: '', last_name: '' };
  }

  const nameParts = trimmedName.split(/\s+/); // Split by any whitespace

  if (nameParts.length === 1) {
    // Single name - treat as first name
    return { first_name: nameParts[0], last_name: '' };
  }

  // Multiple names - last part is last name, everything else is first name
  const lastName = nameParts[nameParts.length - 1];
  const firstName = nameParts.slice(0, -1).join(' ');

  return { first_name: firstName, last_name: lastName };
}

/**
 * Get name components from first_name and last_name
 * Returns the names directly or empty strings if not provided
 */
export function getNameComponents(data: {
  first_name?: string;
  last_name?: string;
}): ParsedName {
  return {
    first_name: data.first_name || '',
    last_name: data.last_name || ''
  };
}
