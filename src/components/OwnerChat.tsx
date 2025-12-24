import { useState } from 'react';
import { ArrowLeft, Send, Car } from 'lucide-react';
import { ChatMessage, Owner } from '../types';

interface OwnerChatProps {
  messages: ChatMessage[];
  owners: Owner[];
  onBack: () => void;
  onSendMessage: (ownerId: string, text: string) => void;
}

export function OwnerChat({ messages, owners, onBack, onSendMessage }: OwnerChatProps) {
  const [selectedOwnerId, setSelectedOwnerId] = useState<string | null>(null);
  const [messageText, setMessageText] = useState('');

  // Group messages by owner
  const ownerChats = owners.map(owner => {
    const ownerMessages = messages.filter(m => m.ownerId === owner.id);
    const lastMessage = ownerMessages[ownerMessages.length - 1];
    const unreadCount = ownerMessages.filter(m => !m.read && m.sender === 'owner').length;
    
    return {
      owner,
      messages: ownerMessages,
      lastMessage,
      unreadCount
    };
  }).filter(chat => chat.messages.length > 0);

  const selectedChat = ownerChats.find(chat => chat.owner.id === selectedOwnerId);

  const handleSendMessage = () => {
    if (messageText.trim() && selectedOwnerId) {
      onSendMessage(selectedOwnerId, messageText);
      setMessageText('');
    }
  };

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-4 py-4 md:px-6">
        <div className="flex items-center gap-3">
          <button
            onClick={selectedOwnerId ? () => setSelectedOwnerId(null) : onBack}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <h1 className="text-gray-900">
            {selectedChat ? selectedChat.owner.name : 'Чат з клієнтами'}
          </h1>
        </div>
        {selectedChat && selectedChat.messages.length > 0 && (
          <div className="mt-2 flex items-center gap-2 text-gray-600">
            <Car className="w-4 h-4" />
            <span className="text-sm">{selectedChat.messages[0].vehiclePlate}</span>
          </div>
        )}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden flex flex-col md:flex-row">
        {/* Chat List - Desktop sidebar or mobile view */}
        <div className={`${selectedOwnerId ? 'hidden md:block' : 'block'} w-full md:w-80 border-r border-gray-200 bg-white overflow-auto`}>
          {ownerChats.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <p>Немає активних чатів</p>
            </div>
          ) : (
            <div>
              {ownerChats.map(chat => (
                <div
                  key={chat.owner.id}
                  onClick={() => setSelectedOwnerId(chat.owner.id)}
                  className={`p-4 border-b border-gray-200 cursor-pointer hover:bg-gray-50 transition-colors ${
                    selectedOwnerId === chat.owner.id ? 'bg-blue-50' : ''
                  }`}
                >
                  <div className="flex items-start justify-between mb-1">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="text-gray-900">{chat.owner.name}</span>
                        {chat.unreadCount > 0 && (
                          <span className="bg-blue-600 text-white text-xs px-2 py-0.5 rounded-full">
                            {chat.unreadCount}
                          </span>
                        )}
                      </div>
                      {chat.lastMessage && (
                        <>
                          <div className="flex items-center gap-1 text-sm text-gray-500 mt-1">
                            <Car className="w-3 h-3" />
                            {chat.lastMessage.vehiclePlate}
                          </div>
                          <p className="text-sm text-gray-600 mt-1 truncate">
                            {chat.lastMessage.sender === 'manager' ? 'Ви: ' : ''}
                            {chat.lastMessage.text}
                          </p>
                        </>
                      )}
                    </div>
                    {chat.lastMessage && (
                      <span className="text-xs text-gray-500">
                        {new Date(chat.lastMessage.timestamp).toLocaleDateString('uk-UA', { 
                          day: 'numeric', 
                          month: 'short' 
                        })}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Chat Messages */}
        <div className={`${selectedOwnerId ? 'flex' : 'hidden md:flex'} flex-1 flex-col`}>
          {selectedChat ? (
            <>
              {/* Messages */}
              <div className="flex-1 overflow-auto p-4 space-y-3">
                {selectedChat.messages.map(message => (
                  <div
                    key={message.id}
                    className={`flex ${message.sender === 'manager' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[70%] px-4 py-2 rounded-lg ${
                        message.sender === 'manager'
                          ? 'bg-blue-600 text-white'
                          : 'bg-white text-gray-900 border border-gray-200'
                      }`}
                    >
                      <p>{message.text}</p>
                      <span className={`text-xs mt-1 block ${
                        message.sender === 'manager' ? 'text-blue-100' : 'text-gray-500'
                      }`}>
                        {new Date(message.timestamp).toLocaleTimeString('uk-UA', { 
                          hour: '2-digit', 
                          minute: '2-digit' 
                        })}
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              {/* Message Input */}
              <div className="bg-white border-t border-gray-200 p-4">
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={messageText}
                    onChange={(e) => setMessageText(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    placeholder="Напишіть повідомлення..."
                    className="flex-1 p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <button
                    onClick={handleSendMessage}
                    disabled={!messageText.trim()}
                    className="bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
                  >
                    <Send className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center text-gray-500">
              <div className="text-center">
                <p>Оберіть чат для початку переписки</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
