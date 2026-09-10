import React, { useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { WelcomeScreen } from './src/screens/WelcomeScreen';
import { LoginScreen } from './src/screens/LoginScreen';
import { SignupScreen } from './src/screens/SignupScreen';
import { OnboardingScreen } from './src/screens/OnboardingScreen';
import { MatchDiscoveryScreen } from './src/screens/MatchDiscoveryScreen';
import { api } from './src/api/client';

type Screen = 'welcome' | 'login' | 'signup' | 'onboarding' | 'matches' | 'loading';

const TOKEN_KEY = '@inconnect_token';

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<Screen>('loading');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | undefined>();
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const storedToken = await AsyncStorage.getItem(TOKEN_KEY);
      if (storedToken) {
        const user = await api.auth.me(storedToken);
        console.log('Logged in as:', user.username);
        setToken(storedToken);
        setCurrentScreen('matches');
      } else {
        setCurrentScreen('welcome');
      }
    } catch {
      setCurrentScreen('welcome');
    }
  };

  const handleLogin = async (username: string, password: string) => {
    setLoading(true);
    setError(undefined);
    try {
      const { token: newToken } = await api.auth.login(username, password);
      await AsyncStorage.setItem(TOKEN_KEY, newToken);
      setToken(newToken);
      console.log('Login successful');
      setCurrentScreen('matches');
    } catch (e: any) {
      setError(e.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleSignup = async (data: {
    firstName: string;
    username: string;
    email: string;
    password1: string;
    password2: string;
  }) => {
    setLoading(true);
    setError(undefined);
    try {
      const { token: newToken } = await api.auth.signup({
        first_name: data.firstName,
        username: data.username,
        email: data.email,
        password1: data.password1,
        password2: data.password2,
      });
      await AsyncStorage.setItem(TOKEN_KEY, newToken);
      setToken(newToken);
      console.log('Signup successful');
      setCurrentScreen('onboarding');
    } catch (e: any) {
      setError(e.message || 'Signup failed');
    } finally {
      setLoading(false);
    }
  };

  const handleOnboardingComplete = () => {
    console.log('Onboarding complete');
    setCurrentScreen('matches');
  };

  const handleLogout = async () => {
    try {
      if (token) {
        await api.auth.logout(token);
      }
    } catch {
      // Ignore logout errors
    } finally {
      await AsyncStorage.removeItem(TOKEN_KEY);
      setToken(null);
      setCurrentScreen('welcome');
    }
  };

  if (currentScreen === 'loading') return null;

  switch (currentScreen) {
    case 'welcome':
      return (
        <WelcomeScreen
          onGetStarted={() => setCurrentScreen('signup')}
          onSignIn={() => setCurrentScreen('login')}
        />
      );
    case 'login':
      return (
        <LoginScreen
          onLogin={handleLogin}
          onSignUp={() => setCurrentScreen('signup')}
          onForgotPassword={() => console.log('Forgot password')}
          loading={loading}
          error={error}
        />
      );
    case 'signup':
      return (
        <SignupScreen
          onSignup={handleSignup}
          onLogin={() => setCurrentScreen('login')}
          loading={loading}
          error={error}
        />
      );
    case 'onboarding':
      return (
        <OnboardingScreen
          token={token!}
          onComplete={handleOnboardingComplete}
          onBack={() => setCurrentScreen('signup')}
        />
      );
    case 'matches':
      return (
        <MatchDiscoveryScreen
          token={token!}
          onViewProfile={(userId) => console.log('View profile:', userId)}
          onMessage={(chatId) => console.log('Message:', chatId)}
          onAddFriend={(userId) => console.log('Add friend:', userId)}
          onBack={handleLogout}
        />
      );
    default:
      return null;
  }
}
