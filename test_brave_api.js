// Simple script to test the Brave Search API directly
import https from 'https';
import zlib from 'zlib';

const BRAVE_API_KEY = "BSAwdg3KjWBtSceDWb776Vj1MacGMZo";
const searchQuery = "What is the weather in New York?";

// Create options for the HTTPS request
const options = {
  hostname: 'api.search.brave.com',
  path: `/res/v1/web/search?q=${encodeURIComponent(searchQuery)}&count=5`,
  method: 'GET',
  headers: {
    'Accept': 'application/json',
    'Accept-Encoding': 'gzip',
    'X-Subscription-Token': BRAVE_API_KEY,
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
  }
};

console.log(`Testing Brave Search API with query: "${searchQuery}"`);
console.log(`Using API key: ${BRAVE_API_KEY.substring(0, 4)}...${BRAVE_API_KEY.substring(BRAVE_API_KEY.length - 4)}`);
console.log(`API endpoint: https://${options.hostname}${options.path}`);

// Make the request
const req = https.request(options, (res) => {
  console.log(`API Response Status: ${res.statusCode}`);
  console.log(`Response Headers: ${JSON.stringify(res.headers)}`);

  // Set up response handling based on encoding
  const encoding = res.headers['content-encoding'];
  let output;

  if (encoding && encoding.includes('gzip')) {
    output = zlib.createGunzip();
    res.pipe(output);
  } else {
    output = res;
  }

  let data = '';

  // Collect data chunks
  output.on('data', (chunk) => {
    data += chunk.toString();
  });

  // Process complete response
  output.on('end', () => {
    console.log('Response received successfully');

    try {
      // Check if it seems like JSON
      if (data.trim().startsWith('{') || data.trim().startsWith('[')) {
        const parsedData = JSON.parse(data);
        console.log('\nComplete API Response:');
        console.log(JSON.stringify(parsedData, null, 2));

        console.log('\nSearch Results Summary:');

        if (parsedData.web && parsedData.web.results) {
          console.log(`Total results: ${parsedData.web.results.length}`);
          console.log('\nFirst 3 results:');
          parsedData.web.results.slice(0, 3).forEach((result, i) => {
            console.log(`\n[${i + 1}] ${result.title}`);
            console.log(`URL: ${result.url}`);
            if (result.description) {
              console.log(`Description: ${result.description.substring(0, 100)}...`);
            }
          });
        } else if (parsedData.error) {
          console.log('Error from API:', parsedData.error);
          console.log('Error type:', parsedData.type);
          console.log('Response time:', parsedData.time);
        } else {
          console.log('No web results found or unexpected format');
          console.log('Response structure:', Object.keys(parsedData));
        }
      } else {
        console.log('Response does not appear to be JSON');
        console.log('Raw response data (first 500 chars):', data.substring(0, 500));
      }
    } catch (e) {
      console.error('Error parsing response:', e.message);
      console.log('Raw response data (first 500 chars):', data.substring(0, 500));
    }
  });
});

// Handle errors
req.on('error', (error) => {
  console.error(`API Request Error: ${error.message}`);
});

// End the request
req.end(); 