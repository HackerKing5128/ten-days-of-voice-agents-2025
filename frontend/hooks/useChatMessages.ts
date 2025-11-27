import { useEffect, useMemo, useState } from 'react';
import { Room, RoomEvent, TranscriptionSegment } from 'livekit-client';
import {
  type ReceivedChatMessage,
  useChat,
  useRoomContext,
} from '@livekit/components-react';

interface TranscriptionMessage {
  id: string;
  timestamp: number;
  text: string;
  participantIdentity: string;
  isFinal: boolean;
}

export function useChatMessages() {
  const chat = useChat();
  const room = useRoomContext();
  const [transcriptions, setTranscriptions] = useState<Map<string, TranscriptionMessage>>(new Map());

  useEffect(() => {
    const handleTranscription = (segments: TranscriptionSegment[]) => {
      setTranscriptions(prev => {
        const updated = new Map(prev);
        segments.forEach(segment => {
          const existing = updated.get(segment.id);
          if (!existing || segment.text.length >= existing.text.length) {
            updated.set(segment.id, {
              id: segment.id,
              timestamp: segment.firstReceivedTime,
              text: segment.text,
              participantIdentity: segment.participant?.identity || 'unknown',
              isFinal: segment.final,
            });
          }
        });
        return updated;
      });
    };

    room.on(RoomEvent.TranscriptionReceived, handleTranscription);
    return () => {
      room.off(RoomEvent.TranscriptionReceived, handleTranscription);
    };
  }, [room]);

  const mergedMessages = useMemo(() => {
    const transcriptionMessages: ReceivedChatMessage[] = Array.from(transcriptions.values()).map(t => ({
      id: t.id,
      timestamp: t.timestamp,
      message: t.text,
      from: t.participantIdentity === room.localParticipant.identity
        ? room.localParticipant
        : Array.from(room.remoteParticipants.values()).find(p => p.identity === t.participantIdentity),
    }));

    const merged = [...transcriptionMessages, ...chat.chatMessages];
    return merged.sort((a, b) => a.timestamp - b.timestamp);
  }, [transcriptions, chat.chatMessages, room]);

  return mergedMessages;
}
