'use client';

import {useRouter} from 'next/navigation';

export default function Home() {
  const router = useRouter();

  return(
  <div title = 'container'>
    <div title = 'logo'>
      <h1>Athletix</h1>
   </div>

   <div title= 'authBtns'>
      <button onClick={()=> router.push('/auth/login')}>login</button>
      <button onClick = {()=> router.push('/auth/signup')}>signup</button>
   </div>
  </div>
   
  );
}