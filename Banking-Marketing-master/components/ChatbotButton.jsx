'use client';

import { useState } from 'react';
import Image from 'next/image';
import Chatbot from './Chatbot';

const ChatbotButton = () => {
  const [isHovered, setIsHovered] = useState(false);
  const [isClicked, setIsClicked] = useState(false);
  const [isChatbotOpen, setIsChatbotOpen] = useState(false);

  const handleClick = () => {
    setIsClicked(true);
    setIsChatbotOpen(true);
    console.log('Chatbot button clicked!');
    
    setTimeout(() => setIsClicked(false), 300);
  };

  const handleCloseChatbot = () => {
    setIsChatbotOpen(false);
  };

  return (
    <>
      {/* Chatbot Modal */}
      {/* {isChatbotOpen && (
        <div className="fixed bottom-40 right-6 z-50">
          <Chatbot onClose={handleCloseChatbot} />
        </div>
     )} */}
      {isChatbotOpen && (
        <>
          {/* Overlay with very light blur */}
          <div className="fixed inset-0 backdrop-blur-[5px] z-5"></div>

          {/* Chatbot modal on top of overlay */}
          <div
            className="fixed bottom-5 right-6 z-50"
            style={{ marginTop: "60px" }}
          >
            <Chatbot onClose={handleCloseChatbot} />
          </div>
        </>
      )}

      {/* Chatbot Button - Only show if chatbot is closed */}
      {!isChatbotOpen && (
        <div className="fixed bottom-16 right-6 z-40">
          <div className="relative">
            <button
              onClick={handleClick}
              onMouseEnter={() => setIsHovered(true)}
              onMouseLeave={() => setIsHovered(false)}
              className={`
                relative w-28 h-28 rounded-full
                transition-all duration-300 ease-in-out
                hover:shadow-xl
                focus:outline-none focus:ring-4 focus:ring-blue-400 focus:ring-opacity-50
                active:scale-95
                ${isHovered ? "scale-110" : "scale-100"}
                ${isClicked ? "scale-90" : ""}
              `}
              aria-label="Open chatbot"
            >
              <div className="relative w-full h-full flex items-center justify-center">
                <div className="absolute inset-0 w-full h-full">
                  <Image
                    src="/assets/outer.png"
                    alt=""
                    width={112}
                    height={112}
                    className="w-full h-full animate-spin"
                    style={{ animationDuration: "6s" }}
                  />
                </div>

                <div className="relative z-10">
                  <Image
                    src="/assets/icon.png"
                    alt="Chatbot"
                    width={60}
                    height={60}
                    className={`
                      transition-transform duration-300
                      ${isHovered ? "scale-110" : "scale-100"}
                    `}
                  />
                </div>
              </div>

              {/* Optional: Tooltip on hover */}
              {isHovered && (
                <div className="absolute bottom-full right-0 mb-2 px-2 py-1 bg-gray-800 text-white text-xs rounded-md shadow-lg whitespace-nowrap z-50">
                  AI Loan Assistant - Get Instant Eligibility
                  <div className="absolute top-full right-3 -mt-1 border-4 border-transparent border-t-gray-800"></div>
                </div>
              )}
            </button>

            {/* "Ask Cogni" text - Positioned with minimal spacing below the button */}
            <div className="absolute top-full left-1/2 transform -translate-x-1/2 mt-1 w-full text-center">
              <span
                className="text-xs font-semibold text-white bg-gradient-to-r from-blue-600 to-purple-600 px-3 py-1.5 rounded-full shadow-md border border-blue-400/30 whitespace-nowrap"
                data-chatbot-button
              >
                Ask Cogni - Loans
              </span>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default ChatbotButton;