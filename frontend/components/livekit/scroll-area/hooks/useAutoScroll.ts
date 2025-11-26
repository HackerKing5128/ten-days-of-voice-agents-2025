import { useEffect, useRef } from 'react';

const AUTO_SCROLL_THRESHOLD_PX = 150;

export function useAutoScroll(scrollContentContainer?: Element | null) {
  const isUserScrolling = useRef(false);
  const scrollTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    function scrollToBottom() {
      if (!scrollContentContainer || isUserScrolling.current) return;

      const distanceFromBottom =
        scrollContentContainer.scrollHeight -
        scrollContentContainer.clientHeight -
        scrollContentContainer.scrollTop;

      // Auto-scroll if user is near the bottom
      if (distanceFromBottom < AUTO_SCROLL_THRESHOLD_PX) {
        requestAnimationFrame(() => {
          if (scrollContentContainer) {
            scrollContentContainer.scrollTop = scrollContentContainer.scrollHeight;
          }
        });
      }
    }

    function handleScroll() {
      if (!scrollContentContainer) return;
      
      const distanceFromBottom =
        scrollContentContainer.scrollHeight -
        scrollContentContainer.clientHeight -
        scrollContentContainer.scrollTop;

      // User is scrolling up - pause auto-scroll
      isUserScrolling.current = distanceFromBottom > AUTO_SCROLL_THRESHOLD_PX;

      // Reset after a short delay if user scrolls back to bottom
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }
      scrollTimeoutRef.current = setTimeout(() => {
        if (distanceFromBottom < AUTO_SCROLL_THRESHOLD_PX) {
          isUserScrolling.current = false;
        }
      }, 150);
    }

    if (scrollContentContainer) {
      // Observe content changes using MutationObserver for real-time updates
      const mutationObserver = new MutationObserver(() => {
        scrollToBottom();
      });

      // Also observe resize for layout changes
      const resizeObserver = new ResizeObserver(scrollToBottom);

      if (scrollContentContainer.firstElementChild) {
        resizeObserver.observe(scrollContentContainer.firstElementChild);
        mutationObserver.observe(scrollContentContainer, {
          childList: true,
          subtree: true,
          characterData: true,
        });
      }

      scrollContentContainer.addEventListener('scroll', handleScroll, { passive: true });
      scrollToBottom();

      return () => {
        resizeObserver.disconnect();
        mutationObserver.disconnect();
        scrollContentContainer.removeEventListener('scroll', handleScroll);
        if (scrollTimeoutRef.current) {
          clearTimeout(scrollTimeoutRef.current);
        }
      };
    }
  }, [scrollContentContainer]);
}
