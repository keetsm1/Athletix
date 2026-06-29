'use client';

import {useRouter} from 'next/navigation';

export default function SignupPage() {
  const router = useRouter();

  return(
  <div title = 'container'>
    <div title = 'logo'>
      <h1>Sign Up</h1>
   </div>   

    <div title = 'signupForm'>
        <input title = 'name' type= "type" placeholder='name'></input>
        <input title= 'email' type = "type" placeholder='email'></input>
        <input title = 'confirmEmail' type = "type" placeholder='re-enter email'></input>
        <input title = 'password' type = "password" placeholder= 'password'></input>
        <input title = 'confirmPassword' type = "password" placeholder= 'Confirm Password'></input>
    </div>
  </div>
     
  );
}
