/**
 * TMX Dashboard - Google Apps Script Proxy
 * 
 * This script serves data from the Google Sheet to the dashboard.
 * Deploy this as a web app to allow the dashboard to fetch live data.
 * 
 * SETUP INSTRUCTIONS:
 * 1. Open Google Sheets: https://docs.google.com/spreadsheets/d/1zOQV8sxFnFQRtp5kvZJJv76DQ_3aqxW1-D-bsEfZK8g
 * 2. Go to Extensions → Apps Script
 * 3. Delete any existing code and paste this entire file
 * 4. Click "Deploy" → "New deployment"
 * 5. Select type: "Web app"
 * 6. Set "Execute as": "Me"
 * 7. Set "Who has access": "Anyone within [your organization]" (e.g., squareup.com)
 * 8. Click "Deploy"
 * 9. Copy the Web App URL and update it in the dashboard HTML
 */

// Configuration
const SHEET_NAME = 'Usage By Event Type (28)';

/**
 * Handle GET requests - serves the sheet data as JSON
 */
function doGet(e) {
  try {
    // Get the active spreadsheet and sheet
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sheet = ss.getSheetByName(SHEET_NAME);
    
    if (!sheet) {
      return createJsonResponse({ error: 'Sheet not found: ' + SHEET_NAME }, 404);
    }
    
    // Get all data from the sheet
    const data = sheet.getDataRange().getValues();
    
    if (data.length < 2) {
      return createJsonResponse({ error: 'No data found in sheet' }, 404);
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
        }
        
        // Ensure events is a number
        obj.events = parseInt(obj.events) || 0;
        
        return obj;
      });
    
    // Return JSON response with CORS headers
    return createJsonResponse({
      success: true,
      count: jsonData.length,
      lastUpdated: new Date().toISOString(),
      data: jsonData
    });
    
  } catch (error) {
    return createJsonResponse({ error: error.toString() }, 500);
  }
}

/**
 * Create a JSON response with proper headers
 */
function createJsonResponse(data, statusCode = 200) {
  const output = ContentService.createTextOutput(JSON.stringify(data))
    .setMimeType(ContentService.MimeType.JSON);
  return output;
}

/**
 * Test function - run this to verify the script works
 */
function testGetData() {
  const result = doGet({});
  Logger.log(result.getContent());
}
