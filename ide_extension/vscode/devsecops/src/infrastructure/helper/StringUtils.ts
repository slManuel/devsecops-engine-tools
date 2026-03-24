/**
 * StringUtils - Utility functions for string manipulation and encoding
 * Consolidates functionality from AuthEncoder and OutputManager
 */
export class StringUtils {
    
    /**
     * Encodes username and password to Base64 for Basic Authentication
     * (consolidated from AuthEncoder)
     * @param username - The username to encode
     * @param password - The password to encode
     * @returns Base64 encoded string
     */
    static encodeBasicAuth(username: string, password: string): string {
        return Buffer.from(`${username}:${password}`).toString('base64');
    }

    /**
     * Removes ANSI escape codes from text
     * (consolidated from OutputManager)
     * @param text - The text containing ANSI codes
     * @returns Clean text without ANSI escape codes
     */
    static removeAnsiEscapeCodes(text: string): string {
        // eslint-disable-next-line no-control-regex
        return text.replace(/\x1b\[[0-9;]*m/g, '');
    }
}
