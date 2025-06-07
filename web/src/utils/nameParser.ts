/**
 * Utility functions for parsing full names into first and last names
 */

export interface ParsedName {
  first_name: string;
  last_name: string;
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
 * Get name components with fallback logic
 * If first_name and last_name are provided, use them directly
 * Otherwise, parse the full_name
 */
export function getNameComponents(data: {
  first_name?: string;
  last_name?: string;
  full_name?: string;
}): ParsedName {
  // If we have both first and last names, use them directly
  if (data.first_name && data.last_name) {
    return { first_name: data.first_name, last_name: data.last_name };
  }

  // If we only have first name, try to get last name from full name
  if (data.first_name && !data.last_name && data.full_name) {
    const parsed = parseFullName(data.full_name);
    // If the parsed first name matches what we have, use the parsed last name
    if (parsed.first_name === data.first_name || data.full_name.startsWith(data.first_name)) {
      return { first_name: data.first_name, last_name: parsed.last_name };
    }
  }

  // If we only have last name, try to get first name from full name
  if (!data.first_name && data.last_name && data.full_name) {
    const parsed = parseFullName(data.full_name);
    // If the parsed last name matches what we have, use the parsed first name
    if (parsed.last_name === data.last_name || data.full_name.endsWith(data.last_name)) {
      return { first_name: parsed.first_name, last_name: data.last_name };
    }
  }

  // Fall back to parsing the full name
  if (data.full_name) {
    return parseFullName(data.full_name);
  }

  // Use whatever we have, or empty strings
  return {
    first_name: data.first_name || '',
    last_name: data.last_name || ''
  };
}
