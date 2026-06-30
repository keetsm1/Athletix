'use client';

import {useRouter} from 'next/navigation';
import { useState, useEffect } from 'react';
import {supabase } from '../../components/supabase/supabase'

export default function SignupPage() {
  const router = useRouter();

  const [email, setEmail] = useState("")
  const [name, setName] = useState("")
  const [confirmEmail, setConfirmEmail] = useState("")
  const [password, setPassword]= useState("")
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError]= useState("")
  const [toast, setToast] = useState<string | null>(null);

  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => setToast(null), 4000);
      return () => clearTimeout(timer);
    }
  }, [toast]);

  const showToast = (msg: string) => {
    setError(msg);
    setToast(msg);
  };

  const signUp = async ()=> {
    if (email !== confirmEmail){
      showToast("Emails do not match");
      return;
    }

    if (password !== confirmPassword){
      showToast("Passwords do not match.");
      return;
    }

    if(password.length < 8 ){
      showToast("Passwords must be at least 8 characters");
      return;
    }

    setLoading(true);

    const {error} = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {display_name : name},
      },
    });

    setLoading(false);

    if (error){
      showToast(error.message);
      return;
    }

    router.push('/auth/login');
  }

  return(
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      {toast && (
        <div className="fixed top-6 left-1/2 -translate-x-1/2 z-50 bg-red-600 text-white px-6 py-3 rounded-lg shadow-lg animate-[fadeIn_0.3s_ease-out]">
          {toast}
        </div>
      )}
      <div className="bg-white rounded-2xl shadow-md w-full max-w-md p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Sign Up</h1>
        </div>

        <div className="space-y-4">
          <input
            type="text"
            placeholder="Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full px-4 py-3 rounded-lg border border-gray-300 text-gray-900 placeholder-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
          />

          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-4 py-3 rounded-lg border border-gray-300 text-gray-900 placeholder-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
          />

          <input
            type="email"
            placeholder="Re-enter email"
            value={confirmEmail}
            onChange={(e) => setConfirmEmail(e.target.value)}
            className="w-full px-4 py-3 rounded-lg border border-gray-300 text-gray-900 placeholder-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
          />

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-3 rounded-lg border border-gray-300 text-gray-900 placeholder-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
          />

          <input
            type="password"
            placeholder="Confirm Password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            className="w-full px-4 py-3 rounded-lg border border-gray-300 text-gray-900 placeholder-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
          />

          <button
            onClick={signUp}
            disabled={loading}
            className="w-full py-3 rounded-lg bg-gray-900 text-white font-semibold hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? "Creating Account..." : "Sign Up"}
          </button>

          <p className="text-center text-sm text-gray-500">
            Already have an account?{' '}
            <button onClick={() => router.push('/auth/login')} className="text-gray-900 font-medium underline">
              Log in
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}
