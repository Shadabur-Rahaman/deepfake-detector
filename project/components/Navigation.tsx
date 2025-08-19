"use client";

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { usePathname } from 'next/navigation';
import { useState } from 'react';
import { motion } from 'framer-motion';
import { Menu, X, Shield, ArrowRight,Camera } from 'lucide-react';

export default function Navigation() {
    const pathname = usePathname();
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    const isActive = (path: string) => pathname === path;

    const navigationItems = [
        { href: '/', label: 'Home' },
        { href: '/features', label: 'Features' },
        { href: '/try-it', label: 'Try It' },
        { href: '/api', label: 'API' },
        { href: '/blog', label: 'Blog' },
        { href: '/contact', label: 'Contact' },
    ];

    return (
        <nav className="border-b bg-white/80 backdrop-blur-md sticky top-0 z-50 shadow-sm">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-16">
                    {/* Logo with Luxurious Animation */}
                    <motion.div
                        className="flex items-center space-x-2"
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.5 }}
                    >
                        <Shield className="h-8 w-8 text-blue-600 hover:text-purple-600 transition-colors duration-300" />
                        <Link href="/" className="text-2xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent hover:scale-105 transition-all duration-300">
                            iFake
                        </Link>
                    </motion.div>

                    {/* Desktop Navigation Links with Luxurious Purple Hover */}
                    <div className="hidden md:flex items-center space-x-8">
                        <Link
                            href="/"
                            className={`relative font-medium transition-all duration-300 hover:scale-105 group px-3 py-2 rounded-lg ${isActive('/')
                                ? 'text-purple-600 bg-gradient-to-r from-purple-50 to-pink-50 shadow-md'
                                : 'text-gray-900 hover:text-white hover:bg-gradient-to-r hover:from-purple-600 hover:via-purple-700 hover:to-pink-600 hover:shadow-lg'
                                }`}
                        >
                            <span className="relative z-10">Home</span>
                            {!isActive('/') && (
                                <div className="absolute inset-0 rounded-lg bg-gradient-to-r from-purple-600 via-purple-700 to-pink-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300 blur-sm -z-10"></div>
                            )}
                        </Link>

                        <Link
                            href="/features"
                            className={`relative font-medium transition-all duration-300 hover:scale-105 group px-3 py-2 rounded-lg ${isActive('/features')
                                ? 'text-purple-600 bg-gradient-to-r from-purple-50 to-pink-50 shadow-md'
                                : 'text-gray-600 hover:text-white hover:bg-gradient-to-r hover:from-purple-600 hover:via-purple-700 hover:to-pink-600 hover:shadow-lg'
                                }`}
                        >
                            <span className="relative z-10">Features</span>
                            {!isActive('/features') && (
                                <div className="absolute inset-0 rounded-lg bg-gradient-to-r from-purple-600 via-purple-700 to-pink-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300 blur-sm -z-10"></div>
                            )}
                        </Link>

                        <Link
                            href="/try-it"
                            className={`relative font-medium transition-all duration-300 hover:scale-105 group px-3 py-2 rounded-lg ${isActive('/try-it')
                                ? 'text-purple-600 bg-gradient-to-r from-purple-50 to-pink-50 shadow-md'
                                : 'text-gray-600 hover:text-white hover:bg-gradient-to-r hover:from-purple-600 hover:via-purple-700 hover:to-pink-600 hover:shadow-lg'
                                }`}
                        >
                            <span className="relative z-10">Try It</span>
                            {!isActive('/try-it') && (
                                <div className="absolute inset-0 rounded-lg bg-gradient-to-r from-purple-600 via-purple-700 to-pink-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300 blur-sm -z-10"></div>
                            )}
                        </Link>
                        <Link
                            href="/real-time-detection"
                            className={`relative font-medium transition-all duration-300 hover:scale-105 group px-3 py-2 rounded-lg ${isActive('/real-time-detection')
                                ? 'text-blue-600 bg-gradient-to-r from-blue-50 to-cyan-50 shadow-md'
                                : 'text-gray-600 hover:text-white hover:bg-gradient-to-r hover:from-blue-600 hover:via-blue-700 hover:to-cyan-600 hover:shadow-lg'
                                }`}
                        >
                            <span className="relative z-10 flex items-center gap-2">
                                <Camera className="w-4 h-4" />
                                🎯 Real-Time Detection
                            </span>
                            {!isActive('/real-time-detection') && (
                                <div className="absolute inset-0 rounded-lg bg-gradient-to-r from-blue-600 via-blue-700 to-cyan-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300 blur-sm -z-10"></div>
                            )}
                        </Link>



                        {/* <Link
                            href="/api"
                            className={`relative font-medium transition-all duration-300 hover:scale-105 group px-3 py-2 rounded-lg ${isActive('/api')
                                ? 'text-purple-600 bg-gradient-to-r from-purple-50 to-pink-50 shadow-md'
                                : 'text-gray-600 hover:text-white hover:bg-gradient-to-r hover:from-purple-600 hover:via-purple-700 hover:to-pink-600 hover:shadow-lg'
                                }`}
                        >
                            <span className="relative z-10">API</span>
                            {!isActive('/api') && (
                                <div className="absolute inset-0 rounded-lg bg-gradient-to-r from-purple-600 via-purple-700 to-pink-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300 blur-sm -z-10"></div>
                            )}
                        </Link> */}

                        <Link
                            href="/blog"
                            className={`relative font-medium transition-all duration-300 hover:scale-105 group px-3 py-2 rounded-lg ${isActive('/blog')
                                ? 'text-purple-600 bg-gradient-to-r from-purple-50 to-pink-50 shadow-md'
                                : 'text-gray-600 hover:text-white hover:bg-gradient-to-r hover:from-purple-600 hover:via-purple-700 hover:to-pink-600 hover:shadow-lg'
                                }`}
                        >
                            <span className="relative z-10">Blog</span>
                            {!isActive('/blog') && (
                                <div className="absolute inset-0 rounded-lg bg-gradient-to-r from-purple-600 via-purple-700 to-pink-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300 blur-sm -z-10"></div>
                            )}
                        </Link>

                        <Link
                            href="/contact"
                            className={`relative font-medium transition-all duration-300 hover:scale-105 group px-3 py-2 rounded-lg ${isActive('/contact')
                                ? 'text-purple-600 bg-gradient-to-r from-purple-50 to-pink-50 shadow-md'
                                : 'text-gray-600 hover:text-white hover:bg-gradient-to-r hover:from-purple-600 hover:via-purple-700 hover:to-pink-600 hover:shadow-lg'
                                }`}
                        >
                            <span className="relative z-10">Contact</span>
                            {!isActive('/contact') && (
                                <div className="absolute inset-0 rounded-lg bg-gradient-to-r from-purple-600 via-purple-700 to-pink-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300 blur-sm -z-10"></div>
                            )}
                        </Link>

                    </div>

                    {/* Premium CTA Button */}
                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.5, delay: 0.2 }}
                        className="hidden md:block"
                    >
                        <Button asChild className="relative bg-gradient-to-r from-purple-600 via-purple-700 to-pink-600 hover:from-purple-700 hover:via-purple-800 hover:to-pink-700 shadow-lg hover:shadow-2xl transition-all duration-300 hover:scale-105 overflow-hidden group">
                            <Link href="/try-it">
                                <span className="relative z-10 flex items-center">
                                    Get Started <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform duration-300" />
                                </span>
                                <div className="absolute inset-0 bg-gradient-to-r from-pink-600 to-purple-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                            </Link>
                        </Button>
                    </motion.div>

                    {/* Mobile Menu Button with Purple Hover */}
                    <div className="md:hidden">
                        <motion.button
                            whileTap={{ scale: 0.95 }}
                            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                            className="p-2 rounded-lg text-gray-600 hover:text-white hover:bg-gradient-to-r hover:from-purple-600 hover:to-pink-600 transition-all duration-300 hover:shadow-lg"
                        >
                            {mobileMenuOpen ? (
                                <X className="h-5 w-5" />
                            ) : (
                                <Menu className="h-5 w-5" />
                            )}
                        </motion.button>
                    </div>
                </div>

                {/* Luxurious Mobile Navigation Menu */}
                {mobileMenuOpen && (
                    <motion.div
                        initial={{ opacity: 0, y: -10, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: -10, scale: 0.95 }}
                        transition={{ duration: 0.3, ease: "easeOut" }}
                        className="md:hidden border-t border-purple-100 bg-gradient-to-br from-white/95 via-purple-50/30 to-pink-50/30 backdrop-blur-md shadow-xl"
                    >
                        <div className="px-4 pt-4 pb-6 space-y-3">
                            {navigationItems.map((item, index) => (
                                <motion.div
                                    key={item.href}
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ duration: 0.3, delay: index * 0.05 }}
                                >
                                    <Link
                                        href={item.href}
                                        className={`block px-4 py-3 rounded-lg text-base font-medium transition-all duration-300 hover:scale-105 ${isActive(item.href)
                                            ? 'text-purple-700 bg-gradient-to-r from-purple-100 to-pink-100 border-l-4 border-purple-600 shadow-md'
                                            : 'text-gray-600 hover:text-white hover:bg-gradient-to-r hover:from-purple-600 hover:via-purple-700 hover:to-pink-600 hover:shadow-lg'
                                            }`}
                                        onClick={() => setMobileMenuOpen(false)}
                                    >
                                        {item.label}
                                    </Link>
                                </motion.div>
                            ))}

                            <motion.div
                                className="pt-4"
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.3, delay: 0.3 }}
                            >
                                <Button asChild className="w-full bg-gradient-to-r from-purple-600 via-purple-700 to-pink-600 hover:from-purple-700 hover:via-purple-800 hover:to-pink-700 shadow-lg hover:shadow-2xl transition-all duration-300 hover:scale-105">
                                    <Link href="/try-it" onClick={() => setMobileMenuOpen(false)}>
                                        Get Started <ArrowRight className="ml-2 h-4 w-4" />
                                    </Link>
                                </Button>
                            </motion.div>
                        </div>
                    </motion.div>
                )}
            </div>
        </nav>
    );
}
