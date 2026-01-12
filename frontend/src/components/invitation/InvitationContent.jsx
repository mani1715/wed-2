import { useEffect, useRef } from 'react';
import { Card } from '@/components/ui/card';
import { Calendar, MapPin, Clock, Heart, Play } from 'lucide-react';

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
      bg: 'bg-gradient-to-br from-orange-50 via-amber-50 to-yellow-50',
      text: 'text-orange-900',
      accent: 'text-orange-600',
      cardBg: 'bg-white/90',
      font: 'font-traditional'
    },
    royal: {
      bg: 'bg-gradient-to-br from-purple-50 via-pink-50 to-amber-50',
      text: 'text-purple-900',
      accent: 'text-purple-600',
      cardBg: 'bg-white/90',
      font: 'font-royal'
    },
    floral: {
      bg: 'bg-gradient-to-br from-rose-50 via-pink-50 to-green-50',
      text: 'text-rose-900',
      accent: 'text-rose-600',
      cardBg: 'bg-white/95',
      font: 'font-elegant'
    },
    divine: {
      bg: 'bg-gradient-to-br from-amber-50 via-white to-gray-50',
      text: 'text-gray-800',
      accent: 'text-amber-600',
      cardBg: 'bg-white/80',
      font: 'font-script'
    },
    cinematic: {
      bg: 'bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900',
      text: 'text-gray-100',
      accent: 'text-amber-400',
      cardBg: 'bg-slate-800/90',
      cardText: 'text-gray-100',
      cardAccent: 'text-amber-400',
      font: 'font-modern'
    },
    scroll: {
      bg: 'bg-gradient-to-br from-amber-100 via-orange-50 to-yellow-50',
      text: 'text-amber-900',
      accent: 'text-amber-700',
      cardBg: 'bg-amber-50/90',
      font: 'font-primary'
    },
    art: {
      bg: 'bg-gradient-to-br from-red-50 via-teal-50 to-purple-50',
      text: 'text-gray-800',
      accent: 'text-red-600',
      cardBg: 'bg-white/90',
      font: 'font-elegant'
    },
    modern: {
      bg: 'bg-gradient-to-br from-blue-50 via-cyan-50 to-pink-50',
      text: 'text-gray-800',
      accent: 'text-blue-600',
      cardBg: 'bg-white/90',
      font: 'font-modern'
    }
  };

  const config = designConfig[design] || designConfig.divine;
  const cardTextColor = config.cardText || config.text;
  const cardAccentColor = config.cardAccent || config.accent;

  const deityImages = {
    ganesha: 'https://images.unsplash.com/photo-1607604760190-ec9ccc12156e',
    venkateswara: 'https://images.unsplash.com/photo-1707833685224-9fcce62dcd3c',
    shiva: 'https://images.unsplash.com/photo-1566890910598-c5768889e83e',
    none: null
  };

  const photoGallery = [
    {
      url: 'https://images.unsplash.com/photo-1720105761832-927de5f2ecce',
      caption: 'Where it all began...'
    },
    {
      url: 'https://images.unsplash.com/photo-1719857646787-38c9c5f79312',
      caption: 'Moments that made us smile'
    },
    {
      url: 'https://images.unsplash.com/photo-1630526720753-aa4e71acf67d',
      caption: 'Traditional love, modern hearts'
    },
    {
      url: 'https://images.unsplash.com/photo-1591969851586-adbbd4accf81',
      caption: 'Every sunset together'
    },
    {
      url: 'https://images.unsplash.com/photo-1556229868-7b2d4b56b909',
      caption: 'Building our forever'
    },
    {
      url: 'https://images.unsplash.com/photo-1559435578-231f6137aac5',
      caption: 'Our journey, our story'
    }
  ];

  return (
    <div className={`min-h-screen ${config.bg} py-12 px-4`}>
      <div className="max-w-4xl mx-auto space-y-16">
        
        {/* SECTION 1: Grand Opening - Already handled by OpeningScreen */}

        {/* SECTION 2: Emotional Welcome Message */}
        <section
          ref={(el) => (sectionsRef.current[0] = el)}
          className="text-center transition-all duration-700 opacity-0"
        >
          <div className={`${config.font} space-y-6 px-4`}>
            <h2 className={`text-3xl md:text-5xl font-semibold ${config.accent} leading-relaxed`}>
              Your Presence Makes Our Celebration Complete
            </h2>
            <p className={`text-xl md:text-2xl ${config.text} italic opacity-90`}>
              Your blessings mean the world to us
            </p>
            <p className={`text-lg md:text-xl ${config.text} opacity-80`}>
              We eagerly await your graceful presence
            </p>
          </div>
        </section>

        {/* SECTION 3: Couple Introduction with Parents */}
        <section
          ref={(el) => (sectionsRef.current[1] = el)}
          className="transition-all duration-700 opacity-0"
        >
          <div className="text-center space-y-8">
            {/* Decorative Divider */}
            <div className="flex items-center justify-center gap-4">
              <div className={`h-px w-20 ${config.accent} bg-current`} />
              <Heart className={`w-6 h-6 ${config.accent}`} fill="currentColor" />
              <div className={`h-px w-20 ${config.accent} bg-current`} />
            </div>

            {/* Bride Section */}
            <div className={`${config.font} space-y-3`}>
              <p className={`text-lg ${config.text} opacity-75`}>Daughter of</p>
              <p className={`text-xl md:text-2xl ${cardTextColor} font-semibold`}>
                Mr. Rajesh Kumar & Mrs. Lakshmi Kumar
              </p>
            </div>

            {/* Couple Names */}
            <div className={`${config.font} my-8`}>
              <h1 className={`text-5xl md:text-7xl lg:text-8xl font-bold ${config.accent} mb-2`}>
                Priya & Arjun
              </h1>
              <div className={`text-2xl md:text-3xl ${config.text} italic mt-4`}>
                Request the honor of your presence
              </div>
            </div>

            {/* Groom Section */}
            <div className={`${config.font} space-y-3`}>
              <p className={`text-lg ${config.text} opacity-75`}>Son of</p>
              <p className={`text-xl md:text-2xl ${cardTextColor} font-semibold`}>
                Mr. Suresh Sharma & Mrs. Anita Sharma
              </p>
            </div>

            {/* Decorative Divider */}
            <div className="flex items-center justify-center gap-4 mt-8">
              <div className={`h-px w-20 ${config.accent} bg-current`} />
              <Heart className={`w-6 h-6 ${config.accent}`} fill="currentColor" />
              <div className={`h-px w-20 ${config.accent} bg-current`} />
            </div>
          </div>
        </section>

        {/* SECTION 4: Love/Union Story */}
        <section
          ref={(el) => (sectionsRef.current[2] = el)}
          className="transition-all duration-700 opacity-0"
        >
          <Card className={`${config.cardBg} backdrop-blur-sm border-none shadow-xl p-8 md:p-12`}>
            <div className={`${config.font} text-center space-y-6`}>
              <h2 className={`text-3xl md:text-4xl font-semibold ${cardAccentColor}`}>
                A Journey of Hearts Becoming One
              </h2>
              <p className={`${cardTextColor} text-lg md:text-xl leading-relaxed opacity-90 max-w-2xl mx-auto`}>
                Two souls, one promise. A bond written by destiny and sealed by love.
                Join us as we begin this beautiful journey of togetherness, blessed by tradition
                and celebrated with joy.
              </p>
              <div className={`text-2xl ${cardAccentColor} italic`}>
                "Two hearts, two souls, forever intertwined"
              </div>
            </div>
          </Card>
        </section>

        {/* SECTION 5: Photo Story Scroll */}
        <section
          ref={(el) => (sectionsRef.current[3] = el)}
          className="transition-all duration-700 opacity-0"
        >
          <div className="text-center mb-8">
            <h2 className={`${config.font} text-3xl md:text-4xl font-semibold ${config.accent} mb-2`}>
              Our Story in Moments
            </h2>
            <p className={`${config.text} text-lg opacity-80`}>
              The journey that led us here...
            </p>
          </div>

          <div className="space-y-8">
            {photoGallery.map((photo, index) => (
              <div
                key={index}
                className="group relative overflow-hidden rounded-2xl shadow-2xl transition-all duration-500 hover:scale-[1.02]"
              >
                <img
                  src={photo.url}
                  alt={photo.caption}
                  className="w-full h-64 md:h-96 object-cover"
                  loading="lazy"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent flex items-end">
                  <p className={`${config.font} text-white text-xl md:text-2xl font-semibold p-6 italic`}>
                    {photo.caption}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* SECTION 6: Pre-Wedding Video */}
        <section
          ref={(el) => (sectionsRef.current[4] = el)}
          className="transition-all duration-700 opacity-0"
        >
          <Card className={`${config.cardBg} backdrop-blur-sm border-none shadow-xl p-8 md:p-12`}>
            <h2 className={`${config.font} text-3xl md:text-4xl font-semibold ${cardAccentColor} text-center mb-6`}>
              Our Pre-Wedding Story
            </h2>
            <div className="relative aspect-video bg-gradient-to-br from-gray-200 to-gray-300 rounded-xl overflow-hidden flex items-center justify-center group cursor-pointer">
              {/* Placeholder for video */}
              <div className="absolute inset-0 bg-gradient-to-br from-purple-900/50 to-pink-900/50 flex flex-col items-center justify-center">
                <Play className="w-20 h-20 text-white mb-4 group-hover:scale-110 transition-transform" />
                <p className="text-white text-xl font-semibold">Watch Our Story</p>
                <p className="text-white/80 text-sm mt-2">(Video coming soon)</p>
              </div>
            </div>
          </Card>
        </section>

        {/* SECTION 7: Event Details */}
        <section
          ref={(el) => (sectionsRef.current[5] = el)}
          className="transition-all duration-700 opacity-0"
        >
          <Card className={`${config.cardBg} backdrop-blur-sm border-none shadow-xl p-8 md:p-12`}>
            <h2 className={`${config.font} text-3xl md:text-4xl font-semibold ${cardAccentColor} text-center mb-8`}>
              Wedding Ceremony
            </h2>

            <div className="space-y-6">
              <div className="flex items-start gap-4">
                <Calendar className={`w-6 h-6 ${cardAccentColor} mt-1 flex-shrink-0`} />
                <div>
                  <div className={`font-semibold ${cardTextColor} text-lg`}>Date</div>
                  <div className={`${cardTextColor} opacity-80`}>Saturday, December 21, 2024</div>
                </div>
              </div>

              <div className="flex items-start gap-4">
                <Clock className={`w-6 h-6 ${cardAccentColor} mt-1 flex-shrink-0`} />
                <div>
                  <div className={`font-semibold ${cardTextColor} text-lg`}>Muhurtham Time</div>
                  <div className={`${cardTextColor} opacity-80`}>10:30 AM - Auspicious Time</div>
                </div>
              </div>

              <div className="flex items-start gap-4">
                <MapPin className={`w-6 h-6 ${cardAccentColor} mt-1 flex-shrink-0`} />
                <div>
                  <div className={`font-semibold ${cardTextColor} text-lg`}>Venue</div>
                  <div className={`${cardTextColor} opacity-80`}>
                    Grand Heritage Wedding Hall<br />
                    123 Main Street, Jubilee Hills<br />
                    Hyderabad, Telangana 500033
                  </div>
                </div>
              </div>
            </div>

            {/* Reception Details */}
            <div className={`mt-8 pt-8 border-t ${cardAccentColor} border-current border-opacity-20`}>
              <h3 className={`${config.font} text-2xl font-semibold ${cardAccentColor} text-center mb-4`}>
                Reception
              </h3>
              <div className={`${cardTextColor} text-center space-y-2`}>
                <p className="text-lg">Join us for dinner and celebrations</p>
                <p className="font-semibold text-xl">Same Day - 7:00 PM Onwards</p>
                <p className="opacity-80">Grand Heritage Wedding Hall</p>
              </div>
            </div>
          </Card>
        </section>

        {/* SECTION 8: Heartfelt Invitation Message */}
        <section
          ref={(el) => (sectionsRef.current[6] = el)}
          className="transition-all duration-700 opacity-0"
        >
          <Card className={`${config.cardBg} backdrop-blur-sm border-none shadow-xl p-8 md:p-12`}>
            <div className={`${config.font} text-center space-y-6`}>
              <h2 className={`text-3xl md:text-5xl font-bold ${cardAccentColor} leading-relaxed`}>
                Your Presence Will Bless Our New Beginning
              </h2>
              <p className={`${cardTextColor} text-xl md:text-2xl opacity-90`}>
                Please join us and make this day unforgettable
              </p>
              <p className={`${cardTextColor} text-lg opacity-80 max-w-2xl mx-auto`}>
                Your love, blessings, and graceful presence mean everything to us as we embark on this
                sacred journey together. We cannot wait to celebrate with you and create memories
                that will last a lifetime.
              </p>
            </div>
          </Card>
        </section>

        {/* SECTION 9: Final Blessing / Closing */}
        <section
          ref={(el) => (sectionsRef.current[7] = el)}
          className="transition-all duration-700 opacity-0 text-center py-12"
        >
          {/* Deity Image if selected */}
          {deity !== 'none' && deityImages[deity] && (
            <div className="mb-8 flex justify-center">
              <div className="relative w-32 h-32 md:w-40 md:h-40 rounded-full overflow-hidden shadow-2xl ring-4 ring-white/50">
                <img
                  src={deityImages[deity]}
                  alt="Divine Blessing"
                  className="w-full h-full object-cover"
                />
              </div>
            </div>
          )}

          <div className={`${config.font} ${config.text} space-y-6`}>
            <p className="text-2xl md:text-3xl font-semibold">
              Seeking Your Blessings and Love
            </p>
            <p className="text-lg md:text-xl opacity-80 italic">
              "May our union be blessed with joy, love, and eternal happiness"
            </p>
          </div>

          {/* Final Decorative Element */}
          <div className="flex justify-center gap-3 mt-8">
            <span className={`text-2xl ${config.accent}`}>✦</span>
            <span className={`text-3xl ${config.accent}`}>❖</span>
            <span className={`text-2xl ${config.accent}`}>✦</span>
          </div>

          {/* Peaceful Closing */}
          <div className={`${config.font} ${config.text} mt-12 opacity-60 text-sm`}>
            <p>With love and gratitude,</p>
            <p className="mt-2">Priya & Arjun's Families</p>
          </div>
        </section>
      </div>
    </div>
  );
};

export default InvitationContent;
