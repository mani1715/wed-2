import { useEffect, useRef } from 'react';
import { Card } from '@/components/ui/card';
import { Calendar, MapPin, Clock, Heart } from 'lucide-react';

export const InvitationContent = ({ design, deity }) => {
  const sectionsRef = useRef([]);

  useEffect(() => {
    // Immediately show first section
    if (sectionsRef.current[0]) {
      sectionsRef.current[0].style.opacity = '1';
      sectionsRef.current[0].classList.add('animate-fade-in-up');
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.classList.add('animate-fade-in-up');
          }
        });
      },
      { threshold: 0.1 }
    );

    sectionsRef.current.forEach((section) => {
      if (section) observer.observe(section);
    });

    return () => observer.disconnect();
  }, []);

  const designConfig = {
    temple: {
      bg: 'bg-temple-background',
      text: 'text-temple-text',
      accent: 'text-temple-accent',
      cardBg: 'bg-white/90',
      font: 'font-traditional'
    },
    royal: {
      bg: 'bg-royal-background',
      text: 'text-royal-text',
      accent: 'text-royal-accent',
      cardBg: 'bg-white/90',
      font: 'font-royal'
    },
    floral: {
      bg: 'bg-floral-background',
      text: 'text-floral-text',
      accent: 'text-floral-accent',
      cardBg: 'bg-white/95',
      font: 'font-elegant'
    },
    divine: {
      bg: 'bg-divine-background',
      text: 'text-divine-text',
      accent: 'text-divine-accent',
      cardBg: 'bg-white/80',
      font: 'font-script'
    },
    cinematic: {
      bg: 'bg-cinematic-background',
      text: 'text-cinematic-text',
      accent: 'text-cinematic-accent',
      cardBg: 'bg-slate-800/80',
      font: 'font-modern'
    },
    scroll: {
      bg: 'bg-scroll-background',
      text: 'text-scroll-text',
      accent: 'text-scroll-accent',
      cardBg: 'bg-amber-50/90',
      font: 'font-primary'
    },
    art: {
      bg: 'bg-art-background',
      text: 'text-art-text',
      accent: 'text-art-accent',
      cardBg: 'bg-white/90',
      font: 'font-elegant'
    },
    modern: {
      bg: 'bg-modern-background',
      text: 'text-modern-text',
      accent: 'text-modern-accent',
      cardBg: 'bg-white/90',
      font: 'font-modern'
    }
  };

  const config = designConfig[design] || designConfig.divine;

  return (
    <div className={`min-h-screen ${config.bg} py-12 px-4`}>
      <div className="max-w-4xl mx-auto space-y-16">
        {/* Header Section */}
        <section
          ref={(el) => (sectionsRef.current[0] = el)}
          className="text-center transition-all duration-700"
        >
          <div className={`${config.font} mb-6`}>
            <div className={`text-sm md:text-base ${config.text} tracking-widest uppercase mb-4`}>
              Together with their families
            </div>
            <h1 className={`text-4xl md:text-6xl lg:text-7xl font-bold ${config.accent} mb-4`}>
              Priya & Arjun
            </h1>
            <div className={`text-xl md:text-2xl ${config.text} italic`}>
              Request the honor of your presence
            </div>
          </div>

          {/* Decorative Divider */}
          <div className="flex items-center justify-center gap-4 my-8">
            <div className={`h-px w-20 ${config.accent} bg-current`} />
            <Heart className={`w-6 h-6 ${config.accent}`} fill="currentColor" />
            <div className={`h-px w-20 ${config.accent} bg-current`} />
          </div>
        </section>

        {/* Event Details */}
        <section
          ref={(el) => (sectionsRef.current[1] = el)}
          className="transition-all duration-700"
        >
          <Card className={`${config.cardBg} backdrop-blur-sm border-none shadow-xl p-8 md:p-12`}>
            <h2 className={`${config.font} text-3xl md:text-4xl font-semibold ${config.accent} text-center mb-8`}>
              Wedding Ceremony
            </h2>

            <div className="space-y-6">
              <div className="flex items-start gap-4">
                <Calendar className={`w-6 h-6 ${config.accent} mt-1 flex-shrink-0`} />
                <div>
                  <div className={`font-semibold ${config.text} text-lg`}>Date</div>
                  <div className={`${config.text} opacity-80`}>Saturday, December 21, 2024</div>
                </div>
              </div>

              <div className="flex items-start gap-4">
                <Clock className={`w-6 h-6 ${config.accent} mt-1 flex-shrink-0`} />
                <div>
                  <div className={`font-semibold ${config.text} text-lg`}>Time</div>
                  <div className={`${config.text} opacity-80`}>10:00 AM - Muhurat</div>
                </div>
              </div>

              <div className="flex items-start gap-4">
                <MapPin className={`w-6 h-6 ${config.accent} mt-1 flex-shrink-0`} />
                <div>
                  <div className={`font-semibold ${config.text} text-lg`}>Venue</div>
                  <div className={`${config.text} opacity-80`}>
                    Grand Heritage Hall<br />
                    123 Main Street, Bangalore<br />
                    Karnataka 560001
                  </div>
                </div>
              </div>
            </div>
          </Card>
        </section>

        {/* Story Section */}
        <section
          ref={(el) => (sectionsRef.current[2] = el)}
          className="transition-all duration-700"
        >
          <Card className={`${config.cardBg} backdrop-blur-sm border-none shadow-xl p-8 md:p-12`}>
            <h2 className={`${config.font} text-3xl md:text-4xl font-semibold ${config.accent} text-center mb-6`}>
              Our Story
            </h2>
            <p className={`${config.text} text-center leading-relaxed text-lg opacity-90`}>
              Two hearts, two souls, and two families coming together to celebrate a love that was written in the stars.
              Join us as we begin this beautiful journey of togetherness.
            </p>
          </Card>
        </section>

        {/* Family Blessings */}
        <section
          ref={(el) => (sectionsRef.current[3] = el)}
          className="transition-all duration-700"
        >
          <div className="grid md:grid-cols-2 gap-6">
            <Card className={`${config.cardBg} backdrop-blur-sm border-none shadow-xl p-8`}>
              <h3 className={`${config.font} text-2xl font-semibold ${config.accent} mb-4 text-center`}>
                Bride's Family
              </h3>
              <div className={`${config.text} text-center space-y-2`}>
                <p className="font-semibold">Mr. Rajesh Kumar & Mrs. Lakshmi Kumar</p>
                <p className="text-sm opacity-80">Parents of the Bride</p>
              </div>
            </Card>

            <Card className={`${config.cardBg} backdrop-blur-sm border-none shadow-xl p-8`}>
              <h3 className={`${config.font} text-2xl font-semibold ${config.accent} mb-4 text-center`}>
                Groom's Family
              </h3>
              <div className={`${config.text} text-center space-y-2`}>
                <p className="font-semibold">Mr. Suresh Sharma & Mrs. Anita Sharma</p>
                <p className="text-sm opacity-80">Parents of the Groom</p>
              </div>
            </Card>
          </div>
        </section>

        {/* Reception Details */}
        <section
          ref={(el) => (sectionsRef.current[4] = el)}
          className="transition-all duration-700"
        >
          <Card className={`${config.cardBg} backdrop-blur-sm border-none shadow-xl p-8 md:p-12`}>
            <h2 className={`${config.font} text-3xl md:text-4xl font-semibold ${config.accent} text-center mb-6`}>
              Reception
            </h2>
            <div className={`${config.text} text-center space-y-4`}>
              <p className="text-lg">Join us for dinner and celebrations</p>
              <p className="font-semibold text-xl">Same Day - 7:00 PM Onwards</p>
              <p className="opacity-80">Grand Heritage Hall, Bangalore</p>
            </div>
          </Card>
        </section>

        {/* Closing Message */}
        <section
          ref={(el) => (sectionsRef.current[5] = el)}
          className="opacity-0 transition-all duration-700 text-center py-8"
        >
          <div className={`${config.font} ${config.text} space-y-4`}>
            <p className="text-2xl md:text-3xl font-semibold">
              Your presence is the greatest gift
            </p>
            <p className="text-lg opacity-80">
              We look forward to celebrating with you
            </p>
          </div>

          {/* Final Decorative Element */}
          <div className="flex justify-center gap-3 mt-8">
            <span className={`text-2xl ${config.accent}`}>✦</span>
            <span className={`text-3xl ${config.accent}`}>❖</span>
            <span className={`text-2xl ${config.accent}`}>✦</span>
          </div>
        </section>
      </div>
    </div>
  );
};

export default InvitationContent;
