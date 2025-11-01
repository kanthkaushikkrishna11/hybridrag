// Utility functions to format responses for better readability

/**
 * Formats raw response text to be more readable
 * Handles table data, lists, and general text formatting
 */
export function formatResponse(rawText: string): string {
  if (!rawText || typeof rawText !== 'string') {
    return 'No response available.';
  }

  let formatted = rawText;

  // Check if it's raw table data (contains lots of | characters)
  const pipeCount = (rawText.match(/\|/g) || []).length;
  
  if (pipeCount > 3) {
    // Likely table data - format it nicely
    formatted = formatTableData(rawText);
  }

  // Ensure proper line breaks
  formatted = formatted.replace(/\n\n+/g, '\n\n');
  
  return formatted.trim();
}

/**
 * Formats table-like data into a readable list
 */
function formatTableData(text: string): string {
  // Pattern: "Value1 | Value2 Value3 | Value4"
  // Split by | and create bullet points
  
  const parts = text.split('|').map(part => part.trim()).filter(part => part);
  
  if (parts.length === 0) {
    return text;
  }

  // Check if it looks like "Country | Year" pattern
  const hasYearPattern = parts.some(part => /\d{4}/.test(part));
  
  if (hasYearPattern) {
    // Format as "• Country (Year)" or similar
    const formatted = parts.map(part => {
      // If part contains both text and year, format nicely
      const yearMatch = part.match(/(\d{4})/);
      if (yearMatch) {
        const country = part.replace(yearMatch[0], '').trim();
        if (country) {
          return `• **${country}** (${yearMatch[0]})`;
        }
        return `• ${yearMatch[0]}`;
      }
      return `• ${part}`;
    });
    
    return formatted.join('\n');
  }
  
  // Generic formatting
  return parts.map(part => `• ${part}`).join('\n');
}

/**
 * Parses markdown-style formatting in text
 */
export function parseMarkdown(text: string): string {
  if (!text) return '';
  
  // Simple markdown parsing
  let parsed = text;
  
  // Bold: **text** or __text__
  parsed = parsed.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  parsed = parsed.replace(/__(.+?)__/g, '<strong>$1</strong>');
  
  // Italic: *text* or _text_
  parsed = parsed.replace(/\*(.+?)\*/g, '<em>$1</em>');
  parsed = parsed.replace(/_(.+?)_/g, '<em>$1</em>');
  
  // Line breaks
  parsed = parsed.replace(/\n/g, '<br/>');
  
  return parsed;
}

/**
 * Checks if response needs formatting
 */
export function needsFormatting(text: string): boolean {
  if (!text) return false;
  
  // Check for indicators of raw data
  const indicators = [
    /\|.*\|.*\|/, // Multiple pipes (table data)
    /^[A-Z][a-z]+\s*\|\s*\d{4}/, // Country | Year pattern
    /Query Results:/i, // Raw query results header
  ];
  
  return indicators.some(pattern => pattern.test(text));
}

