// Simple script to test the Google Maps Places API directly
import https from 'https';

const GOOGLE_MAPS_API_KEY = "AIzaSyB2kxDjle7yKIVJjoNVKw5vMkENy9TljQQ";
const searchQuery = "pizza near New York";

// Create options for the HTTPS request
const options = {
  hostname: 'maps.googleapis.com',
  path: `/maps/api/place/textsearch/json?query=${encodeURIComponent(searchQuery)}&key=${GOOGLE_MAPS_API_KEY}`,
  method: 'GET',
  headers: {
    'Accept': 'application/json'
  }
};

console.log(`Testing Google Maps Places API with query: "${searchQuery}"`);
console.log(`Using API key: ${GOOGLE_MAPS_API_KEY.substring(0, 4)}...${GOOGLE_MAPS_API_KEY.substring(GOOGLE_MAPS_API_KEY.length - 4)}`);
console.log(`API endpoint: https://${options.hostname}${options.path}`);

// Make the request
const req = https.request(options, (res) => {
  console.log(`API Response Status: ${res.statusCode}`);
  console.log(`Response Headers: ${JSON.stringify(res.headers)}`);

  let data = '';

  // Collect data chunks
  res.on('data', (chunk) => {
    data += chunk.toString();
  });

  // Process complete response
  res.on('end', () => {
    console.log('Response received successfully');

    try {
      // Parse JSON response
      const parsedData = JSON.parse(data);
      console.log('\nComplete API Response:');
      console.log(JSON.stringify(parsedData, null, 2));

      // Check status
      if (parsedData.status) {
        console.log(`\nAPI Status: ${parsedData.status}`);

        if (parsedData.status === 'OK') {
          console.log('\nSearch Results Summary:');
          if (parsedData.results && parsedData.results.length > 0) {
            console.log(`Total results: ${parsedData.results.length}`);
            console.log('\nFirst 3 results:');
            parsedData.results.slice(0, 3).forEach((result, i) => {
              console.log(`\n[${i + 1}] ${result.name}`);
              console.log(`Address: ${result.formatted_address}`);
              if (result.rating) {
                console.log(`Rating: ${result.rating}/5 (${result.user_ratings_total} reviews)`);
              }
            });
          } else {
            console.log('No results found');
          }
        } else if (parsedData.error_message) {
          console.log(`Error message: ${parsedData.error_message}`);
        }
      } else {
        console.log('Unexpected response format - no status field');
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