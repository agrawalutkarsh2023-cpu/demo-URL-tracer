import { Link } from 'react-router-dom';
import { Shield, ChevronRight, FileText } from 'lucide-react';
import usePageMeta from '../hooks/usePageMeta';

export default function PrivacyPolicy() {
  usePageMeta(
    'Privacy Policy',
    'NetTrace Security privacy policy. This is a demo prototype — no real user data, credentials, or production network data is collected or stored.'
  );

  const sections = [
    {
      title: '1. Overview',
      body: `URL-Tracer is a hackathon demo prototype for a URL-Based Cyber Attack Detection & IP Intelligence System. 
This application operates entirely on synthetic, simulated data. No real user traffic, 
government data, production network packets, or personal information is processed.`,
    },
    {
      title: '2. Data We Collect',
      body: `This demo prototype does NOT collect:
• Real IP addresses or network traffic
• Personal credentials or authentication data
• Browser history or tracking cookies
• Any personally identifiable information (PII)

The application uses only synthetic / fictional records generated at startup for demonstration purposes.`,
    },
    {
      title: '3. Cookies & Local Storage',
      body: `This application does not use tracking cookies. No third-party analytics (Google Analytics, Mixpanel, etc.) 
are embedded. Any state stored in the browser (e.g., session state) is temporary and contains 
no sensitive data.`,
    },
    {
      title: '4. Synthetic Data Disclaimer',
      body: `All IP addresses displayed are from RFC 1918 private ranges (10.x.x.x, 172.16.x.x, 192.168.x.x) 
and are entirely fictional. All attack records, geolocation data, and detection results are 
machine-generated for demonstration purposes only. No real victims, attackers, or 
infrastructure are represented.`,
    },
    {
      title: '5. Third-Party Services',
      body: `This prototype may load fonts from Google Fonts (fonts.googleapis.com). Google's own privacy 
policy governs that interaction. No other third-party services receive any data from this application.`,
    },
    {
      title: '6. Contact & Enquiries',
      body: `If you submit a message through our contact form, it is processed locally within this demo 
environment only. No data is transmitted to any external server. For questions about this 
prototype, use the contact form on the Contact page.`,
    },
    {
      title: '7. Changes to This Policy',
      body: `This privacy policy may be updated as the prototype evolves. The last updated date is 
displayed below. Continued use of the demo after changes constitutes acceptance of the 
updated policy.`,
    },
  ];

  return (
    <div className="min-h-screen bg-dark-950 px-4 py-12">
      <div className="max-w-3xl mx-auto animate-fade-in">

        {/* Header */}
        <div className="mb-8">
          <nav aria-label="breadcrumb" className="flex items-center gap-1.5 text-xs text-slate-600 mb-4">
            <Link to="/" className="hover:text-cyber-400 transition-colors">Home</Link>
            <ChevronRight className="w-3 h-3" />
            <span className="text-slate-400">Privacy Policy</span>
          </nav>

          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-xl bg-cyber-600/15 border border-cyber-500/30
                            flex items-center justify-center">
              <FileText className="w-5 h-5 text-cyber-400" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Privacy Policy</h1>
              <p className="text-xs text-slate-500 font-mono mt-0.5">Last updated: August 18, 2026</p>
            </div>
          </div>

          {/* Demo notice */}
          <div className="flex items-start gap-3 p-4 rounded-xl bg-amber-500/8 border border-amber-500/20">
            <Shield className="w-4 h-4 text-amber-400 mt-0.5 flex-shrink-0" />
            <p className="text-xs text-amber-300/80 leading-relaxed">
              <span className="font-semibold text-amber-400">Demo Prototype Notice:</span>{' '}
              This application uses 100% synthetic data. No real IPDR, credentials, government data,
              or user information is ever stored or transmitted.
            </p>
          </div>
        </div>

        {/* Sections */}
        <div className="space-y-6">
          {sections.map((s) => (
            <div key={s.title} className="glass-card p-6">
              <h2 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-cyber-400 flex-shrink-0" />
                {s.title}
              </h2>
              <p className="text-sm text-slate-400 leading-relaxed whitespace-pre-line">{s.body}</p>
            </div>
          ))}
        </div>

        {/* Footer links */}
        <div className="mt-10 pt-6 border-t border-dark-700/50 flex flex-wrap items-center gap-4 text-xs text-slate-600">
          <Link to="/" className="hover:text-cyber-400 transition-colors">← Back to Dashboard</Link>
          <Link to="/contact" className="hover:text-cyber-400 transition-colors">Contact Us</Link>
          <span className="ml-auto font-mono">URL-Tracer · Demo Prototype · v1.0</span>
        </div>
      </div>
    </div>
  );
}
