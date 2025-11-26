import { useEffect, useState, useRef } from 'react';
import { Room, RoomEvent, TranscriptionSegment, Participant } from 'livekit-client';
import {
  type ReceivedChatMessage,
  useChat,
  useRoomContext,
} from '@livekit/components-react';

interface TranscriptionMessage {
  id: string;
  text: string;
  timestamp: number;
  participantIdentity: string;
  isFinal: boolean;
}

export function useChatMessages(): ReceivedChatMessage[] {
  const chat = useChat();
  const room = useRoomContext();
  const [transcriptionMessages, setTranscriptionMessages] = useState<Map<string, TranscriptionMessage>>(new Map());
  const lastUpdateRef = useRef<number>(0);

  // Listen directly to room transcription events
  useEffect(() => {
    if (!room) return;

    const handleTranscription = (
      segments: TranscriptionSegment[],
      participant?: Participant
    ) => {
      const now = Date.now();
      // Throttle updates to prevent too many re-renders
      if (now - lastUpdateRef.current < 50) return;
      lastUpdateRef.current = now;

      setTranscriptionMessages(prev => {
        const newMap = new Map(prev);
        
        segments.forEach(segment => {
          const existingMsg = newMap.get(segment.id);
          
          // Only update if text is longer (more complete) or if it's final
          if (!existingMsg || segment.text.length >= existingMsg.text.length || segment.final) {
            newMap.set(segment.id, {
              id: segment.id,
              text: segment.text,
              timestamp: segment.firstReceivedTime,
              participantIdentity: participant?.identity || 'unknown',
              isFinal: segment.final,
            });
          }
        });
        
        return newMap;
      });
    };

    room.on(RoomEvent.TranscriptionReceived, handleTranscription);

    return () => {
      room.off(RoomEvent.TranscriptionReceived, handleTranscription);
    };
  }, [room]);

  // Convert transcription messages to ReceivedChatMessage format
  const messages: ReceivedChatMessage[] = [];

  // Add transcription messages
  transcriptionMessages.forEach((msg) => {
    const participant = msg.participantIdentity === room.localParticipant.identity
      ? room.localParticipant
      : Array.from(room.remoteParticipants.values()).find(
          (p) => p.identity === msg.participantIdentity
        );
    
    messages.push({
      id: msg.id,
      timestamp: msg.timestamp,
      message: msg.text,
      type: 'chatMessage' as const,
      from: participant,
    });
  });

  // Add chat messages
  chat.chatMessages.forEach(msg => {
    // Avoid duplicates
    if (!messages.some(m => m.id === msg.id)) {
      messages.push(msg);
    }
  });

  // Sort by timestamp
  return messages.sort((a, b) => a.timestamp - b.timestamp);
}
