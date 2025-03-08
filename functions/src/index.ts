//
import { onRequest } from 'firebase-functions/v2/https'; //version 2

// Ts Types
type indexable = { [key: string]: any }; //onject of key string, value any

//Function name helloworld , Event type Https Request
export const helloworld = onRequest((request, response) => {
  debugger; //to use debugger chrome inspect tools
  //Call back (Custom code after event trigger)
  const name = request.params[0].replace('/', ''); //params (name) first item

  const dbFruits: indexable = {
    banana: 'this is banana MONKEY!! AHAHHAH',
    carrow: 'this is carrot',
  };
  //ts dont know shape of name
  const valueMessage = dbFruits[name]; //get same name of request from db

  response.send(`<h2>${valueMessage}</h2>`); //respond by sending a the msg value

  //response is msg
});
