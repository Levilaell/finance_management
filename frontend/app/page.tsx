'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { useAuthStore } from '@/store/auth-store';
import { useEffect } from 'react';
import { 
  ChartBarIcon, 
  BanknotesIcon, 
  DocumentChartBarIcon,
  ShieldCheckIcon,
  CreditCardIcon,
  ChartPieIcon
} from '@heroicons/react/24/outline';

export default function Home() {
  const { isAuthenticated, isLoading } = useAuthStore();
  const router = useRouter();

  // Removed automatic redirect to dashboard - users can choose when to go to dashboard

  const features = [
    {
      name: 'Bank Account Integration',
      description: 'Connect and sync all your bank accounts in one place.',
      icon: CreditCardIcon,
    },
    {
      name: 'Transaction Management',
      description: 'Automatically categorize and track all your transactions.',
      icon: BanknotesIcon,
    },
    {
      name: 'Financial Reports',
      description: 'Generate comprehensive reports for better insights.',
      icon: DocumentChartBarIcon,
    },
    {
      name: 'Real-time Analytics',
      description: 'Monitor your financial health with live dashboards.',
      icon: ChartBarIcon,
    },
    {
      name: 'Smart Categories',
      description: 'AI-powered transaction categorization for accuracy.',
      icon: ChartPieIcon,
    },
    {
      name: 'Secure & Private',
      description: 'Bank-level security with end-to-end encryption.',
      icon: ShieldCheckIcon,
    },
  ];

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* Header */}
      <header className="container mx-auto px-4 py-6">
        <nav className="flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <ChartBarIcon className="h-8 w-8 text-primary" />
            <span className="text-2xl font-bold text-gray-900">FinanceHub</span>
          </div>
          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <Link href="/dashboard">
                <Button>Go to Dashboard</Button>
              </Link>
            ) : (
              <>
                <Link href="/login">
                  <Button variant="ghost">Login</Button>
                </Link>
                <Link href="/register">
                  <Button>Get Started</Button>
                </Link>
              </>
            )}
          </div>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20">
        <div className="text-center max-w-4xl mx-auto">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Take Control of Your Business Finances
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            All-in-one financial management platform that helps you track expenses, 
            manage cash flow, and make data-driven decisions.
          </p>
          <div className="flex justify-center space-x-4">
            <Link href="/register">
              <Button size="lg" className="px-8">
                Start Free Trial
              </Button>
            </Link>
            <Link href="#features">
              <Button size="lg" variant="outline" className="px-8">
                Learn More
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="container mx-auto px-4 py-20">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Everything you need to manage your finances
          </h2>
          <p className="text-lg text-gray-600">
            Powerful features designed for modern businesses
          </p>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature) => (
            <div
              key={feature.name}
              className="bg-white p-6 rounded-lg shadow-lg hover:shadow-xl transition-shadow"
            >
              <div className="flex items-center mb-4">
                <feature.icon className="h-8 w-8 text-primary" />
                <h3 className="ml-3 text-xl font-semibold text-gray-900">
                  {feature.name}
                </h3>
              </div>
              <p className="text-gray-600">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-primary py-20">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to streamline your finances?
          </h2>
          <p className="text-xl text-white/90 mb-8">
            Join thousands of businesses already using FinanceHub
          </p>
          <Link href="/register">
            <Button size="lg" variant="secondary" className="px-8">
              Start Your Free Trial
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <ChartBarIcon className="h-8 w-8" />
                <span className="text-xl font-bold">FinanceHub</span>
              </div>
              <p className="text-gray-400">
                Simplifying financial management for businesses worldwide.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="#features" className="hover:text-white">Features</Link></li>
                <li><Link href="#" className="hover:text-white">Pricing</Link></li>
                <li><Link href="#" className="hover:text-white">Security</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="#" className="hover:text-white">About</Link></li>
                <li><Link href="#" className="hover:text-white">Blog</Link></li>
                <li><Link href="#" className="hover:text-white">Careers</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Support</h4>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="#" className="hover:text-white">Help Center</Link></li>
                <li><Link href="#" className="hover:text-white">Contact</Link></li>
                <li><Link href="#" className="hover:text-white">Status</Link></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 FinanceHub. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}