import {onRequest, onCall} from "firebase-functions/v2/https"; // 1.version 2
import { analyzeReceipt as analyzeReceiptEmulator } from "./receiptService";


// to export this function as callable for front end
// TODO: CORS DONT WORK ON DIRECT CALLS, USE STORAGE
export const analyzeReceipt = onCall({cors:true},async(request)=>{
const file = request.data //file as arg (receipt)

try{
  const result = await analyzeReceiptEmulator(file) //analyze receipt
  return{success:true, data:result} 
}catch(e:any){
  console.log("Error in analyze receipt emulator ", e)
  return {success:false ,error: e.message||"Unknown error"}
}
});


// // Ts Types
// type indexable = { [key: string]: any }; // onject of key string, value any

// // 2. Function name helloworld ,3. Event type Https Request
// export const helloworld = onRequest((request, response) => {
//   debugger; // debugger for chrome inspect tools

//   // 4. Call back (Custom code after event trigger)
//   const name = request.params[0].replace("/", ""); // params (name) first item

//   const dbFruits: indexable = {
//     banana: "this is banana MONKEY!! AHAHHAH",
//     carrow: "this is carrot",
//   };
//   // ts dont know shape of name
//   const valueMessage = dbFruits[name]; // get same name of request from db

//   response.send(`<h2>${valueMessage}</h2>`); // respond by sending a the msg value

//   // response is msg
// });
