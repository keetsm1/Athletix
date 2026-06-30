'use client';

import {useRouter} from 'next/navigation';
import { useState } from 'react';
import {supabase} from '../../components/supabase/supabase'

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const signIn = async () => {
    setLoading(true);
    const {error} = await supabase.auth.signInWithPassword({email, password});
    setLoading(false);
    if (!error) router.push('/');
  };

  return(
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="bg-white rounded-2xl shadow-md w-full max-w-md p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Login</h1>
        </div>

        <div className="space-y-4">
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-4 py-3 rounded-lg border border-gray-300 text-gray-900 placeholder-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
          />

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-3 rounded-lg border border-gray-300 text-gray-900 placeholder-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
          />

          <button
            onClick={signIn}
            disabled={loading}
            className="w-full py-3 rounded-lg bg-gray-900 text-white font-semibold hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? "Logging in..." : "Log In"}
          </button>

          <p className="text-center text-sm text-gray-500">
            Don't have an account?{' '}
            <button onClick={() => router.push('/auth/signup')} className="text-gray-900 font-medium underline">
              Sign up
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}
