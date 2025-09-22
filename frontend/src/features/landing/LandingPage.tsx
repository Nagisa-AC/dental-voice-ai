import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Card, FormGroup, Input, Select } from '../../components';
import './LandingPage.css';

const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const [showCookieBanner, setShowCookieBanner] = useState(true);
  const [isScrolled, setIsScrolled] = useState(false);
  const [activeTestimonial, setActiveTestimonial] = useState(0);
  const [showRequestDemo, setShowRequestDemo] = useState(false);
  const [showViewDemo, setShowViewDemo] = useState(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    practice: '',
    industry: 'dental', // Default to dental but support others
    message: ''
  });
  const headerRef = useRef<HTMLElement>(null);

  const testimonials = [
    {
      name: "Dr. Sarah Johnson",
      role: "Dental Practice Owner",
      practice: "Bright Smile Dentistry",
      content: "Healthcare Voice AI answers every phone call, even after hours. We went from missing 30% of calls to missing zero. New patient bookings increased 40%.",
      rating: 5,
      metric: "40% more bookings"
    },
    {
      name: "Dr. Michael Chen",
      role: "Family Medicine Physician",
      practice: "Wellness Family Care",
      content: "Our voice AI handles 80% of phone calls and appointment scheduling. Patients love being able to call anytime and our staff can focus on patient care.",
      rating: 5,
      metric: "80% automation"
    },
    {
      name: "Dr. Emily Rodriguez",
      role: "Veterinary Clinic Owner",
      practice: "Paws & Claws Animal Hospital",
      content: "Even for veterinary care, Healthcare Voice AI works perfectly. Pet owners appreciate being able to call and schedule appointments anytime.",
      rating: 5,
      metric: "24/7 availability"
    },
    {
      name: "Dr. Lisa Thompson",
      role: "Mental Health Therapist",
      practice: "Mindful Counseling Center",
      content: "Healthcare Voice AI helps us manage appointment scheduling while maintaining patient privacy. Our clients can book sessions at their convenience.",
      rating: 5,
      metric: "100% privacy"
    },
    {
      name: "Dr. James Wilson",
      role: "Cardiologist",
      practice: "Heart Care Specialists",
      content: "The voice AI understands medical terminology and can handle complex appointment scheduling. It's like having a medical receptionist available 24/7.",
      rating: 5,
      metric: "Medical expertise"
    }
  ];

  // Handle scroll effect for navbar
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Enhanced scroll handling with intersection observer
  useEffect(() => {
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animate-fade-in-up');
        }
      });
    }, observerOptions);

    const elements = document.querySelectorAll('.benefit-card, .feature-card, .industry-card, .testimonial-card');
    elements.forEach((el) => observer.observe(el));

    return () => observer.disconnect();
  }, []);

  // Auto-rotate testimonials
  useEffect(() => {
    const interval = setInterval(() => {
      setActiveTestimonial((prev) => (prev + 1) % testimonials.length);
    }, 5000);
    return () => clearInterval(interval);
  }, [testimonials.length]);

  const handleViewDemo = () => {
    setShowViewDemo(true);
  };

  const handleRequestDemo = () => {
    setShowRequestDemo(true);
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle form submission
    console.log('Form submitted:', formData);
    setShowRequestDemo(false);
    // Reset form
    setFormData({
      name: '',
      email: '',
      phone: '',
      practice: '',
      industry: 'dental',
      message: ''
    });
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSmoothScroll = (targetId: string) => {
    const element = document.getElementById(targetId);
    if (element) {
      element.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }
  };


  const healthcareIndustries = [
    {
      value: 'dental',
      name: 'Dental',
      icon: (
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="dentalGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#4f46e5" />
              <stop offset="100%" stopColor="#6366f1" />
            </linearGradient>
          </defs>
          <path d="M12 2C8.7 2 6 4.7 6 8V14C6 17.3 8.7 20 12 20C15.3 20 18 17.3 18 14V8C18 4.7 15.3 2 12 2ZM16 14C16 16.2 14.2 18 12 18C9.8 18 8 16.2 8 14V8C8 5.8 9.8 4 12 4C14.2 4 16 5.8 16 8V14ZM10 9H14V11H10V9ZM11 12H13V16H11V12Z" fill="url(#dentalGradient)"/>
        </svg>
      )
    },
    {
      value: 'family_medicine',
      name: 'Family Medicine',
      icon: (
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="familyGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#4f46e5" />
              <stop offset="100%" stopColor="#6366f1" />
            </linearGradient>
          </defs>
          <path d="M12 2C8.59 2 5.85 4.74 5.85 8.15C5.85 11.56 12 22 12 22S18.15 11.56 18.15 8.15C18.15 4.74 15.41 2 12 2ZM12 11C10.34 11 9 9.66 9 8S10.34 5 12 5S15 6.34 15 8S13.66 11 12 11ZM14.5 1C13.5 1 12.75 1.75 12.75 2.75S13.5 4.5 14.5 4.5S16.25 3.75 16.25 2.75S15.5 1 14.5 1Z" fill="url(#familyGradient)"/>
        </svg>
      )
    },
    {
      value: 'dermatology',
      name: 'Dermatology',
      icon: (
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="dermGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#4f46e5" />
              <stop offset="100%" stopColor="#6366f1" />
            </linearGradient>
          </defs>
          <path d="M12 2C13.1 2 14 2.9 14 4V6H16C17.1 6 18 6.9 18 8V10H20C21.1 10 22 10.9 22 12V18C22 19.1 21.1 20 20 20H14C12.9 20 12 19.1 12 18V4C12 2.9 12.9 2 12 2ZM10 8C10.6 8 11 8.4 11 9S10.6 10 10 10S9 9.6 9 9S9.4 8 10 8ZM8 12C8.6 12 9 12.4 9 13S8.6 14 8 14S7 13.6 7 13S7.4 12 8 12ZM6 16C6.6 16 7 16.4 7 17S6.6 18 6 18S5 17.6 5 17S5.4 16 6 16Z" fill="url(#dermGradient)"/>
        </svg>
      )
    },
    {
      value: 'cardiology',
      name: 'Cardiology',
      icon: (
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="cardioGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#4f46e5" />
              <stop offset="100%" stopColor="#6366f1" />
            </linearGradient>
          </defs>
          <path d="M12 21.35L10.55 20.03C5.4 15.36 2 12.27 2 8.5C2 5.41 4.42 3 7.5 3C9.24 3 10.91 3.81 12 5.08C13.09 3.81 14.76 3 16.5 3C19.58 3 22 5.41 22 8.5C22 12.27 18.6 15.36 13.45 20.03L12 21.35Z" fill="url(#cardioGradient)"/>
        </svg>
      )
    },
    {
      value: 'orthopedics',
      name: 'Orthopedics',
      icon: (
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="orthoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#4f46e5" />
              <stop offset="100%" stopColor="#6366f1" />
            </linearGradient>
          </defs>
          <path d="M18 2C19.1 2 20 2.9 20 4C20 5.1 19.1 6 18 6H16V8H18C19.1 8 20 8.9 20 10C20 11.1 19.1 12 18 12H16V14H18C19.1 14 20 14.9 20 16C20 17.1 19.1 18 18 18H16V20C16 21.1 15.1 22 14 22H10C8.9 22 8 21.1 8 20V18H6C4.9 18 4 17.1 4 16C4 14.9 4.9 14 6 14H8V12H6C4.9 12 4 11.1 4 10C4 8.9 4.9 8 6 8H8V6H6C4.9 6 4 5.1 4 4C4 2.9 4.9 2 6 2C7.1 2 8 2.9 8 4V6H10V4C10 2.9 10.9 2 12 2H18Z" fill="url(#orthoGradient)"/>
        </svg>
      )
    },
    {
      value: 'mental_health',
      name: 'Mental Health',
      icon: (
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="mentalGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#4f46e5" />
              <stop offset="100%" stopColor="#6366f1" />
            </linearGradient>
          </defs>
          <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2ZM19 7C20.1 7 21 7.9 21 9V15C21 16.1 20.1 17 19 17H17V19C17 20.1 16.1 21 15 21H9C7.9 21 7 20.1 7 19V17H5C3.9 17 3 16.1 3 15V9C3 7.9 3.9 7 5 7H7V5C7 3.9 7.9 3 9 3H15C16.1 3 17 3.9 17 5V7H19ZM15 5H9V7H15V5ZM19 9H5V15H7V13H9V15H15V13H17V15H19V9Z" fill="url(#mentalGradient)"/>
        </svg>
      )
    },
    {
      value: 'veterinary',
      name: 'Veterinary',
      icon: (
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="vetGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#4f46e5" />
              <stop offset="100%" stopColor="#6366f1" />
            </linearGradient>
          </defs>
          <path d="M12 8C13.1 8 14 8.9 14 10C14 11.1 13.1 12 12 12C10.9 12 10 11.1 10 10C10 8.9 10.9 8 12 8ZM8.5 7C9.3 7 10 7.7 10 8.5C10 9.3 9.3 10 8.5 10C7.7 10 7 9.3 7 8.5C7 7.7 7.7 7 8.5 7ZM15.5 7C16.3 7 17 7.7 17 8.5C17 9.3 16.3 10 15.5 10C14.7 10 14 9.3 14 8.5C14 7.7 14.7 7 15.5 7ZM6 11C6.8 11 7.5 11.7 7.5 12.5C7.5 13.3 6.8 14 6 14C5.2 14 4.5 13.3 4.5 12.5C4.5 11.7 5.2 11 6 11ZM18 11C18.8 11 19.5 11.7 19.5 12.5C19.5 13.3 18.8 14 18 14C17.2 14 16.5 13.3 16.5 12.5C16.5 11.7 17.2 11 18 11ZM12 14C14.2 14 16 15.8 16 18V20C16 20.6 15.6 21 15 21H9C8.4 21 8 20.6 8 20V18C8 15.8 9.8 14 12 14Z" fill="url(#vetGradient)"/>
        </svg>
      )
    }
  ];

  const keyBenefits = [
    {
      icon: (
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="phoneGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#4f46e5" />
              <stop offset="100%" stopColor="#6366f1" />
            </linearGradient>
          </defs>
          <path d="M6.62 10.79C8.06 13.62 10.38 15.94 13.21 17.38L15.41 15.18C15.69 14.9 16.08 14.82 16.43 14.93C17.55 15.3 18.75 15.5 20 15.5C20.55 15.5 21 15.95 21 16.5V20C21 20.55 20.55 21 20 21C10.61 21 3 13.39 3 4C3 3.45 3.45 3 4 3H7.5C8.05 3 8.5 3.45 8.5 4C8.5 5.25 8.7 6.45 9.07 7.57C9.18 7.92 9.1 8.31 8.82 8.59L6.62 10.79Z" fill="url(#phoneGradient)"/>
        </svg>
      ),
      title: "Never Miss a Call",
      description: "Voice AI answers every phone call 24/7, even when your office is closed"
    },
    {
      icon: (
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="chartGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#10b981" />
              <stop offset="100%" stopColor="#059669" />
            </linearGradient>
          </defs>
          <path d="M16 6L18.29 8.29L13.41 13.17L9.41 9.17L2 16.59L3.41 18L9.41 12L13.41 16L19.71 9.71L22 12V6H16Z" fill="url(#chartGradient)"/>
        </svg>
      ),
      title: "40% More Bookings",
      description: "AI converts more callers into appointments by being available when patients call"
    },
    {
      icon: (
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="clockGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#f59e0b" />
              <stop offset="100%" stopColor="#d97706" />
            </linearGradient>
          </defs>
          <path d="M13 2.05V5.08C16.39 5.57 19 8.47 19 12C19 15.53 16.39 18.43 13 18.92V21.95C18.39 21.45 22 17.19 22 12C22 6.81 18.39 2.55 13 2.05M11 2.05C5.61 2.55 2 6.81 2 12C2 17.19 5.61 21.45 11 21.95V18.92C7.61 18.43 5 15.53 5 12C5 8.47 7.61 5.57 11 5.08V2.05Z" fill="url(#clockGradient)"/>
        </svg>
      ),
      title: "Setup in 24 Hours",
      description: "Get your voice assistant answering calls in less than a day"
    }
  ];

  const features = [
    {
      title: "Voice Call Handling",
      description: "AI voice assistant answers phone calls and understands medical terminology",
      benefits: ["24/7 phone coverage", "Natural conversation", "Medical terminology trained"]
    },
    {
      title: "Phone-Based Scheduling",
      description: "Patients can book appointments directly through phone calls",
      benefits: ["Real-time availability", "Calendar integration", "Appointment confirmation"]
    },
    {
      title: "Industry-Specific Voice AI",
      description: "Voice assistant trained for each healthcare specialty",
      benefits: ["Dental procedures", "Mental health protocols", "Veterinary care"]
    },
    {
      title: "HIPAA Compliant Calls",
      description: "Secure voice calls protecting patient information",
      benefits: ["Encrypted calls", "Audit trails", "Compliance monitoring"]
    }
  ];

  return (
    <div className="landing-page">
      {/* Cookie Banner */}
      {showCookieBanner && (
        <div className="cookie-banner">
          <div className="cookie-content">
            <p>We use cookies to enhance your experience. <a href="#" style={{color: '#3b82f6'}}>Learn more</a></p>
            <button className="cookie-accept" onClick={() => setShowCookieBanner(false)}>Accept</button>
          </div>
        </div>
      )}

      {/* Header */}
      <header ref={headerRef} className={`header ${isScrolled ? 'scrolled' : ''}`}>
        <nav className="nav">
          <a href="/" className="logo">
            <span className="logo-icon">🏥</span>
            <span className="logo-text">DentaFlow</span>
          </a>
          <ul className={`nav-links ${isMenuOpen ? 'open' : ''}`}>
            <li><a href="#features" className="nav-link" onClick={() => handleSmoothScroll('features')}>Features</a></li>
            <li><a href="#pricing" className="nav-link" onClick={() => handleSmoothScroll('pricing')}>Pricing</a></li>
            <li><a href="#testimonials" className="nav-link" onClick={() => handleSmoothScroll('testimonials')}>Testimonials</a></li>
            <li><a href="#about" className="nav-link" onClick={() => handleSmoothScroll('about')}>About</a></li>
          </ul>
          <div className="nav-actions">
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => navigate('/login')}
              className="btn-nav btn-nav-secondary"
            >
              Sign In
            </Button>
            <Button 
              variant="primary" 
              size="sm" 
              onClick={handleRequestDemo}
              className="btn-nav btn-nav-primary"
            >
              Get Started
            </Button>
            <button 
              className="mobile-menu-toggle"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              aria-label="Toggle menu"
            >
              <span></span>
              <span></span>
              <span></span>
            </button>
          </div>
        </nav>
      </header>


      {/* Hero Section */}
      <section className="hero">
        <div className="hero-container">
          <div className="hero-content">
            <div className="hero-badge">
              <span className="badge-icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 2L15.09 8.26L22 9L17 14L18.18 21L12 17.77L5.82 21L7 14L2 9L8.91 8.26L12 2Z" fill="currentColor"/>
                </svg>
              </span>
              <span>Trusted by 500+ Healthcare Practices</span>
            </div>
            <h1 className="hero-title">
              Stop Missing Phone Calls.
              <span className="gradient-text"> Start Growing Your Practice.</span>
            </h1>
            <p className="hero-subtitle">
              AI-powered voice assistants that answer your phone 24/7, never miss a call, and convert 40% more callers into appointments. 
              Set up in 24 hours, see results immediately.
            </p>
            <div className="hero-actions">
              <button className="btn-primary" onClick={handleRequestDemo}>
                Start Free Trial
                <span className="btn-badge">No credit card required</span>
              </button>
              <button className="btn-secondary" onClick={handleViewDemo}>
                Listen to Demo Call
              </button>
            </div>
            <div className="hero-stats">
              <div className="stat">
                <span className="stat-number">40%</span>
                <span className="stat-label">More Bookings</span>
              </div>
              <div className="stat">
                <span className="stat-number">60%</span>
                <span className="stat-label">Less Admin Work</span>
              </div>
              <div className="stat">
                <span className="stat-number">24hrs</span>
                <span className="stat-label">Setup Time</span>
              </div>
            </div>
          </div>
                 <div className="hero-visual">
                   <div className="hero-demo">
                     <div className="demo-header">
                       <div className="call-info">
                         <div className="call-avatar">
                           <div className="avatar-ring">
                             <div className="avatar-pulse"></div>
                             <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                               <path d="M6.62 10.79C8.06 13.62 10.38 15.94 13.21 17.38L15.41 15.18C15.69 14.9 16.08 14.82 16.43 14.93C17.55 15.3 18.75 15.5 20 15.5C20.55 15.5 21 15.95 21 16.5V20C21 20.55 20.55 21 20 21C10.61 21 3 13.39 3 4C3 3.45 3.45 3 4 3H7.5C8.05 3 8.5 3.45 8.5 4C8.5 5.25 8.7 6.45 9.07 7.57C9.18 7.92 9.1 8.31 8.82 8.59L6.62 10.79Z" fill="currentColor"/>
                             </svg>
                           </div>
                         </div>
                         <div className="call-details">
                           <h4>DentaFlow AI</h4>
                           <p>Voice Assistant</p>
                         </div>
                       </div>
                       <div className="call-status">
                         <div className="status-indicator">
                           <div className="status-dot live-pulse"></div>
                           <span>LIVE</span>
                         </div>
                         <div className="call-duration">02:34</div>
                       </div>
                     </div>
              <div className="demo-conversation">
                <div className="conversation-item ai">
                  <div className="conversation-avatar">
                    <div className="avatar-ring-small">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M6.62 10.79C8.06 13.62 10.38 15.94 13.21 17.38L15.41 15.18C15.69 14.9 16.08 14.82 16.43 14.93C17.55 15.3 18.75 15.5 20 15.5C20.55 15.5 21 15.95 21 16.5V20C21 20.55 20.55 21 20 21C10.61 21 3 13.39 3 4C3 3.45 3.45 3 4 3H7.5C8.05 3 8.5 3.45 8.5 4C8.5 5.25 8.7 6.45 9.07 7.57C9.18 7.92 9.1 8.31 8.82 8.59L6.62 10.79Z" fill="currentColor"/>
                      </svg>
                    </div>
                  </div>
                  <div className="conversation-bubble ai-bubble">
                    <div className="voice-waveform">
                      <div className="wave-bar"></div>
                      <div className="wave-bar"></div>
                      <div className="wave-bar"></div>
                      <div className="wave-bar"></div>
                      <div className="wave-bar"></div>
                    </div>
                    <p>Good morning! Thank you for calling Bright Smile Dentistry. I'm your AI assistant. How can I help you today?</p>
                    <span className="conversation-time">2:34 PM</span>
                  </div>
                </div>
                <div className="conversation-item user">
                  <div className="conversation-bubble user-bubble">
                    <div className="voice-waveform user-wave">
                      <div className="wave-bar"></div>
                      <div className="wave-bar"></div>
                      <div className="wave-bar"></div>
                      <div className="wave-bar"></div>
                      <div className="wave-bar"></div>
                    </div>
                    <p>Hi, I'd like to schedule a dental cleaning appointment.</p>
                    <span className="conversation-time">2:35 PM</span>
                  </div>
                  <div className="conversation-avatar user-avatar">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M12 12C14.21 12 16 10.21 16 8C16 5.79 14.21 4 12 4C9.79 4 8 5.79 8 8C8 10.21 9.79 12 12 12ZM12 14C9.33 14 4 15.34 4 18V20H20V18C20 15.34 14.67 14 12 14Z" fill="currentColor"/>
                    </svg>
                  </div>
                </div>
                <div className="conversation-item ai">
                  <div className="conversation-avatar">
                    <div className="avatar-ring-small">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M6.62 10.79C8.06 13.62 10.38 15.94 13.21 17.38L15.41 15.18C15.69 14.9 16.08 14.82 16.43 14.93C17.55 15.3 18.75 15.5 20 15.5C20.55 15.5 21 15.95 21 16.5V20C21 20.55 20.55 21 20 21C10.61 21 3 13.39 3 4C3 3.45 3.45 3 4 3H7.5C8.05 3 8.5 3.45 8.5 4C8.5 5.25 8.7 6.45 9.07 7.57C9.18 7.92 9.1 8.31 8.82 8.59L6.62 10.79Z" fill="currentColor"/>
                      </svg>
                    </div>
                  </div>
                  <div className="conversation-bubble ai-bubble">
                    <div className="voice-waveform">
                      <div className="wave-bar"></div>
                      <div className="wave-bar"></div>
                      <div className="wave-bar"></div>
                      <div className="wave-bar"></div>
                      <div className="wave-bar"></div>
                    </div>
                    <p>Perfect! I have several openings this week. Would Tuesday at 2:00 PM work for you?</p>
                    <span className="conversation-time">2:36 PM</span>
                  </div>
                </div>
                <div className="conversation-item user">
                  <div className="conversation-bubble user-bubble">
                    <div className="voice-waveform user-wave">
                      <div className="wave-bar"></div>
                      <div className="wave-bar"></div>
                      <div className="wave-bar"></div>
                      <div className="wave-bar"></div>
                      <div className="wave-bar"></div>
                    </div>
                    <p>Yes, that works great!</p>
                    <span className="conversation-time">2:36 PM</span>
                  </div>
                  <div className="conversation-avatar user-avatar">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M12 12C14.21 12 16 10.21 16 8C16 5.79 14.21 4 12 4C9.79 4 8 5.79 8 8C8 10.21 9.79 12 12 12ZM12 14C9.33 14 4 15.34 4 18V20H20V18C20 15.34 14.67 14 12 14Z" fill="currentColor"/>
                    </svg>
                  </div>
                </div>
                <div className="conversation-item ai">
                  <div className="conversation-avatar">
                    <div className="avatar-ring-small">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M6.62 10.79C8.06 13.62 10.38 15.94 13.21 17.38L15.41 15.18C15.69 14.9 16.08 14.82 16.43 14.93C17.55 15.3 18.75 15.5 20 15.5C20.55 15.5 21 15.95 21 16.5V20C21 20.55 20.55 21 20 21C10.61 21 3 13.39 3 4C3 3.45 3.45 3 4 3H7.5C8.05 3 8.5 3.45 8.5 4C8.5 5.25 8.7 6.45 9.07 7.57C9.18 7.92 9.1 8.31 8.82 8.59L6.62 10.79Z" fill="currentColor"/>
                      </svg>
                    </div>
                  </div>
                  <div className="conversation-bubble ai-bubble">
                    <div className="voice-waveform">
                      <div className="wave-bar"></div>
                      <div className="wave-bar"></div>
                      <div className="wave-bar"></div>
                      <div className="wave-bar"></div>
                      <div className="wave-bar"></div>
                    </div>
                    <p>Excellent! I've booked your cleaning for Tuesday at 2:00 PM. You'll receive a confirmation text shortly. Is there anything else I can help you with?</p>
                    <span className="conversation-time">2:37 PM</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Key Benefits Section */}
      <section id="benefits" className="benefits">
        <div className="container">
          <div className="section-header">
            <h2>Why Healthcare Practices Choose DentaFlow</h2>
            <p>Never miss another phone call. Our voice AI answers every call, every time.</p>
          </div>
          <div className="benefits-grid">
            {keyBenefits.map((benefit, index) => (
              <div key={benefit.title} className="benefit-card" style={{ animationDelay: `${index * 0.1}s` }}>
                <div className="benefit-icon">{benefit.icon}</div>
                <h3>{benefit.title}</h3>
                <p>{benefit.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Industries Section */}
      <section id="industries" className="industries">
        <div className="container">
          <div className="section-header">
            <h2>Built for Every Healthcare Specialty</h2>
            <p>Industry-specific voice AI training for better phone conversations.</p>
          </div>
          <div className="industries-grid">
            {healthcareIndustries.map((industry, index) => (
              <div key={industry.value} className="industry-card" style={{ animationDelay: `${index * 0.1}s` }}>
                <div className="industry-icon">{industry.icon}</div>
                <h3>{industry.name}</h3>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="features">
        <div className="container">
          <div className="section-header">
            <h2>Everything You Need to Never Miss a Call</h2>
            <p>Voice AI features designed specifically for healthcare phone systems.</p>
          </div>
          <div className="features-grid">
            {features.map((feature, index) => (
              <div key={feature.title} className="feature-card" style={{ animationDelay: `${index * 0.1}s` }}>
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
                <ul className="feature-benefits">
                  {feature.benefits.map((benefit, benefitIndex) => (
                    <li key={benefitIndex}>{benefit}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" className="testimonials">
        <div className="container">
          <div className="section-header">
            <h2>What Healthcare Professionals Say</h2>
            <p>Real results from practices using DentaFlow's voice AI.</p>
          </div>
          <div className="testimonials-container">
            <div className="testimonial-card active">
              <div className="testimonial-content">
                <div className="testimonial-metric">
                  <span className="metric-number">{testimonials[activeTestimonial].metric}</span>
                </div>
                <div className="testimonial-rating">
                  {[...Array(testimonials[activeTestimonial].rating)].map((_, i) => (
                    <span key={i} className="star">⭐</span>
                  ))}
                </div>
                <blockquote>"{testimonials[activeTestimonial].content}"</blockquote>
                <div className="testimonial-author">
                  <div className="author-info">
                    <h4>{testimonials[activeTestimonial].name}</h4>
                    <p>{testimonials[activeTestimonial].role}</p>
                    <span className="practice-name">{testimonials[activeTestimonial].practice}</span>
                  </div>
                </div>
              </div>
            </div>
            <div className="testimonial-dots">
              {testimonials.map((_, index) => (
                <button
                  key={index}
                  className={`dot ${index === activeTestimonial ? 'active' : ''}`}
                  onClick={() => setActiveTestimonial(index)}
                />
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="pricing">
        <div className="container">
          <div className="section-header">
            <h2>Simple Pricing That Scales</h2>
            <p>Start free, scale as you grow. No hidden fees, no long-term contracts.</p>
          </div>
          <div className="pricing-grid">
            <div className="pricing-card">
              <div className="pricing-header">
                <h3>Starter</h3>
                <div className="price">
                  <span className="currency">$</span>
                  <span className="amount">99</span>
                  <span className="period">/month</span>
                </div>
                <p className="price-description">Perfect for small practices</p>
              </div>
              <ul className="pricing-features">
                <li>Up to 500 phone calls/month</li>
                <li>Basic voice AI assistant</li>
                <li>Calendar integration</li>
                <li>Email support</li>
                <li>30-day free trial</li>
              </ul>
              <button className="btn-pricing" onClick={handleRequestDemo}>Start Free Trial</button>
            </div>
            <div className="pricing-card featured">
              <div className="pricing-badge">Most Popular</div>
              <div className="pricing-header">
                <h3>Professional</h3>
                <div className="price">
                  <span className="currency">$</span>
                  <span className="amount">199</span>
                  <span className="period">/month</span>
                </div>
                <p className="price-description">For growing practices</p>
              </div>
              <ul className="pricing-features">
                <li>Up to 2,000 phone calls/month</li>
                <li>Advanced voice AI assistant</li>
                <li>Industry-specific training</li>
                <li>Call analytics dashboard</li>
                <li>Priority support</li>
                <li>30-day free trial</li>
              </ul>
              <button className="btn-pricing" onClick={handleRequestDemo}>Start Free Trial</button>
            </div>
            <div className="pricing-card">
              <div className="pricing-header">
                <h3>Enterprise</h3>
                <div className="price">
                  <span className="currency">$</span>
                  <span className="amount">399</span>
                  <span className="period">/month</span>
                </div>
                <p className="price-description">For large practices</p>
              </div>
              <ul className="pricing-features">
                <li>Unlimited phone calls</li>
                <li>Custom voice AI training</li>
                <li>Multi-location support</li>
                <li>Advanced phone integrations</li>
                <li>Dedicated support</li>
                <li>30-day free trial</li>
              </ul>
              <button className="btn-pricing" onClick={handleRequestDemo}>Contact Sales</button>
            </div>
          </div>
                <div className="pricing-guarantee">
                  <p>
                    <span className="guarantee-item">
                      <span className="guarantee-icon">✓</span>
                      30-day free trial
                    </span>
                    <span className="guarantee-item">
                      <span className="guarantee-icon">✓</span>
                      No setup fees
                    </span>
                    <span className="guarantee-item">
                      <span className="guarantee-icon">✓</span>
                      Cancel anytime
                    </span>
                  </p>
                </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta">
        <div className="container">
          <div className="cta-content">
            <h2>Ready to Stop Missing Phone Calls?</h2>
            <p>Join 500+ healthcare practices already using DentaFlow's voice AI to never miss another call.</p>
            <div className="cta-actions">
              <button className="btn-primary" onClick={handleRequestDemo}>
                Start Free Trial
                <span className="btn-badge">No credit card required</span>
              </button>
              <button className="btn-secondary" onClick={handleViewDemo}>
                Listen to Demo
              </button>
            </div>
            <div className="cta-trust">
              <p>Trusted by healthcare professionals nationwide</p>
              <div className="trust-badges">
                <span className="trust-badge">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                      <linearGradient id="hipaaGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#4f46e5" />
                        <stop offset="100%" stopColor="#6366f1" />
                      </linearGradient>
                    </defs>
                    <path d="M12 2C13.1 2 14 2.9 14 4V6H16C17.1 6 18 6.9 18 8V10H20C21.1 10 22 10.9 22 12V18C22 19.1 21.1 20 20 20H14C12.9 20 12 19.1 12 18V4C12 2.9 12.9 2 12 2ZM10 8C10.6 8 11 8.4 11 9S10.6 10 10 10S9 9.6 9 9S9.4 8 10 8ZM8 12C8.6 12 9 12.4 9 13S8.6 14 8 14S7 13.6 7 13S7.4 12 8 12ZM6 16C6.6 16 7 16.4 7 17S6.6 18 6 18S5 17.6 5 17S5.4 16 6 16Z" fill="url(#hipaaGradient)"/>
                  </svg>
                  HIPAA Compliant
                </span>
                <span className="trust-badge">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                      <linearGradient id="socGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#4f46e5" />
                        <stop offset="100%" stopColor="#6366f1" />
                      </linearGradient>
                    </defs>
                    <path d="M12 1L3 5V11C3 16.55 6.84 21.74 12 23C17.16 21.74 21 16.55 21 11V5L12 1ZM10 17L5 12L6.41 10.59L10 14.17L17.59 6.58L19 8L10 17Z" fill="url(#socGradient)"/>
                  </svg>
                  SOC 2 Certified
                </span>
                <span className="trust-badge">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                      <linearGradient id="ratingGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#4f46e5" />
                        <stop offset="100%" stopColor="#6366f1" />
                      </linearGradient>
                    </defs>
                    <path d="M12 17.27L18.18 21L16.54 13.97L22 9.24L14.81 8.62L12 2L9.19 8.62L2 9.24L7.46 13.97L5.82 21L12 17.27Z" fill="url(#ratingGradient)"/>
                  </svg>
                  4.9/5 Rating
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-section">
              <div className="footer-logo">
                <span className="logo-icon">🏥</span>
                <span className="logo-text">DentaFlow</span>
              </div>
              <p>AI-powered voice assistants for healthcare practices across all medical specialties.</p>
            </div>
            <div className="footer-section">
              <h4>Product</h4>
              <ul>
                <li><a href="#features">Features</a></li>
                <li><a href="#industries">Industries</a></li>
                <li><a href="#pricing">Pricing</a></li>
                <li><a href="#">Integrations</a></li>
              </ul>
            </div>
            <div className="footer-section">
              <h4>Company</h4>
              <ul>
                <li><a href="#">About</a></li>
                <li><a href="#">Blog</a></li>
                <li><a href="#">Careers</a></li>
                <li><a href="#">Contact</a></li>
              </ul>
            </div>
            <div className="footer-section">
              <h4>Support</h4>
              <ul>
                <li><a href="#">Help Center</a></li>
                <li><a href="#">Documentation</a></li>
                <li><a href="#">Status</a></li>
                <li><a href="#">Security</a></li>
              </ul>
            </div>
          </div>
          <div className="footer-bottom">
            <p>&copy; 2024 DentaFlow. All rights reserved.</p>
            <div className="footer-links">
              <a href="#">Privacy Policy</a>
              <a href="#">Terms of Service</a>
              <a href="#">HIPAA Compliance</a>
            </div>
          </div>
        </div>
      </footer>

      {/* Demo Modal */}
      {showRequestDemo && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h3>Start Your Free Trial</h3>
              <button className="modal-close" onClick={() => setShowRequestDemo(false)}>×</button>
            </div>
            <form onSubmit={handleFormSubmit} className="modal-form">
              <div className="form-group">
                <label>Full Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>Practice Name</label>
                <input
                  type="text"
                  value={formData.practice}
                  onChange={(e) => setFormData({...formData, practice: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>Healthcare Industry</label>
                <select
                  value={formData.industry}
                  onChange={(e) => setFormData({...formData, industry: e.target.value})}
                  required
                >
                  {healthcareIndustries.map((industry) => (
                    <option key={industry.value} value={industry.value}>
                      {industry.icon} {industry.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Phone Number</label>
                <input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => setFormData({...formData, phone: e.target.value})}
                />
              </div>
              <button type="submit" className="btn-primary">Start Free Trial</button>
              <p className="form-disclaimer">No credit card required • 30-day free trial • Cancel anytime</p>
            </form>
          </div>
        </div>
      )}

      {/* View Demo Modal */}
      {showViewDemo && (
        <div className="modal-overlay" onClick={() => setShowViewDemo(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Listen to Demo Call</h3>
              <button className="modal-close" onClick={() => setShowViewDemo(false)}>×</button>
            </div>
            <div style={{textAlign: 'center', padding: '2rem 0'}}>
              <div style={{fontSize: '3rem', marginBottom: '1rem'}}>📞</div>
              <h4 style={{marginBottom: '1rem', color: '#1e293b'}}>Experience Our Voice AI</h4>
              <p style={{color: '#64748b', marginBottom: '2rem', lineHeight: '1.6'}}>
                Listen to how our AI voice assistant handles real patient calls, 
                schedules appointments, and provides helpful information.
              </p>
              <div style={{background: '#f8fafc', padding: '1.5rem', borderRadius: '0.75rem', marginBottom: '2rem'}}>
                <p style={{fontStyle: 'italic', color: '#475569'}}>
                  "Good morning! Thank you for calling Bright Smile Dentistry. 
                  I'm your AI assistant. How can I help you today?"
                </p>
              </div>
              <button 
                className="btn-primary" 
                onClick={() => {
                  // Play demo audio or navigate to demo page
                  alert('Demo call would play here');
                }}
                style={{width: '100%'}}
              >
                ▶️ Play Demo Call
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LandingPage;