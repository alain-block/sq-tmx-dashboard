/**
 * TMX Dashboard - Standalone Google Apps Script
 * 
 * This is a STANDALONE script that reads from the Google Sheet
 * without modifying the sheet itself.
 * 
 * SETUP INSTRUCTIONS:
 * 1. Go to https://script.google.com/home
 * 2. Click "New project"
 * 3. Delete any existing code and paste this entire file
 * 4. Click "Save" and name the project "TMX Dashboard API"
 * 5. Click "Deploy" → "New deployment"
 * 6. Select type: "Web app"
 * 7. Set "Execute as": "Me"
 * 8. Set "Who has access": "Anyone within [your organization]"
 * 9. Click "Deploy" and authorize when prompted
 * 10. Copy the Web App URL and paste it into the dashboard
 */

// Configuration - The Google Sheet to read from
const SPREADSHEET_ID = '1zOQV8sxFnFQRtp5kvZJJv76DQ_3aqxW1-D-bsEfZK8g';
const SHEET_NAME = 'Usage By Event Type (28)';

/**
 * Handle GET requests - serves the sheet data as JSON
 */
function doGet(e) {
  try {
    // Open the spreadsheet by ID (doesn't modify it)
    const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
    const sheet = ss.getSheetByName(SHEET_NAME);
    
    if (!sheet) {
      return createJsonResponse({ 
        success: false,
        error: 'Sheet not found: ' + SHEET_NAME 
      });
    }
    
    // Get all data from the sheet (read-only operation)
    const data = sheet.getDataRange().getValues();
    
    if (data.length < 2) {
      return createJsonResponse({ 
        success: false,
        error: 'No data found in sheet' 
      });
    }
    
    // Parse headers and rows
    const headers = data[0];
    const rows = data.slice(1);
    
    // Convert to array of objects
    const jsonData = rows
      .filter(row => row[0] && row[2] !== 'N/A') // Filter out empty rows and N/A
      .map(row => {
        const obj = {};
        headers.forEach((header, index) => {
          // Normalize header names
          let key = header.toString().toLowerCase().replace(/\s+/g, '_');
          if (key === 'event_type') key = 'eventType';
          obj[key] = row[index];
        });
        
        // Format date as YYYY-MM-DD string
        if (obj.date instanceof Date) {
          obj.date = Utilities.formatDate(obj.date, Session.getScriptTimeZone(), 'yyyy-MM-dd');
        } else if (typeof obj.date === 'string') {
          // Already a string, keep it
        } else if (typeof obj.date === 'number') {
          // Excel serial date number - convert it
          const date = new Date((obj.date - 25569) * 86400 * 1000);
          obj.date = Utilities.formatDate(date, Session.getScriptTimeZone(), 'yyyy-MM-dd');
        }
        
        // Ensure events is a number
        obj.events = parseInt(obj.events) || 0;
        
        return obj;
      });
    
    // Return JSON response
    return createJsonResponse({
      success: true,
      count: jsonData.length,
      lastUpdated: new Date().toISOString(),
      sheetName: SHEET_NAME,
      data: jsonData
    });
    
  } catch (error) {
    return createJsonResponse({ 
      success: false,
      error: error.toString() 
    });
  }
}

/**
 * Create a JSON response with proper CORS headers
 */
function createJsonResponse(data) {
  return ContentService.createTextOutput(JSON.stringify(data))
    .setMimeType(ContentService.MimeType.JSON);
}

/**
 * Test function - run this in the Apps Script editor to verify it works
 * Go to "Run" → "testGetData" to test
 */
function testGetData() {
  const result = doGet({});
  const content = result.getContent();
  const parsed = JSON.parse(content);
  
  Logger.log('Success: ' + parsed.success);
  Logger.log('Record count: ' + parsed.count);
  
  if (parsed.data && parsed.data.length > 0) {
    Logger.log('First record: ' + JSON.stringify(parsed.data[0]));
    Logger.log('Last record: ' + JSON.stringify(parsed.data[parsed.data.length - 1]));
  }
  
  if (parsed.error) {
    Logger.log('Error: ' + parsed.error);
  }
}
