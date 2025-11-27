import { useState, useEffect, useCallback } from 'react';
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

export function useChatMessages() {
  const chat = useChat();
  const room = useRoomContext();
  const [transcriptions, setTranscriptions] = useState<Map<string, TranscriptionMessage>>(new Map());

  const handleTranscription = useCallback((
    segments: TranscriptionSegment[],
    participant?: Participant
  ) => {
    if (!participant) return;
    
    // Debug log to verify transcriptions are received
    console.log('[Chat] Transcription received:', segments.length, 'segments from', participant.identity);
    
    setTranscriptions(prev => {
      const newMap = new Map(prev);
      
      for (const segment of segments) {
        const existingMessage = newMap.get(segment.id);
        
        if (!existingMessage || segment.final || segment.text.length > existingMessage.text.length) {
          newMap.set(segment.id, {
            id: segment.id,
            text: segment.text,
            timestamp: segment.firstReceivedTime,
            participantIdentity: participant.identity,
            isFinal: segment.final,
          });
        }
      }
      
      return newMap;
    });
  }, []);

  useEffect(() => {
    if (!room) return;

    room.on(RoomEvent.TranscriptionReceived, handleTranscription);
    
    return () => {
      room.off(RoomEvent.TranscriptionReceived, handleTranscription);
    };
  }, [room, handleTranscription]);

  const transcriptionMessages: ReceivedChatMessage[] = Array.from(transcriptions.values()).map(t => ({
    id: t.id,
    timestamp: t.timestamp,
    message: t.text,
    from: t.participantIdentity === room?.localParticipant?.identity
      ? room.localParticipant
      : Array.from(room?.remoteParticipants?.values() || []).find(
          (p) => p.identity === t.participantIdentity
        ),
  }));

  const merged: ReceivedChatMessage[] = [
    ...transcriptionMessages,
    ...chat.chatMessages,
  ].sort((a, b) => a.timestamp - b.timestamp);

  return merged;
}
