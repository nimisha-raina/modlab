/* Keep the original H5P buttons and handlers, but give them a non-scrolling
   footer. H5P's inline height estimates must never clip the next action. */
window.LessonQuestionLayout = {
  install(doc, root) {
    const phases = new WeakMap();
    function arrange() {
      root.querySelectorAll('.h5p-dialog[data-lib="H5P.MultiChoice"]').forEach(dialog => {
        let footer = dialog.querySelector('.lesson-question-actions');
        // H5P reuses this dialog for the next question. Prefer its newly attached
        // buttons and discard the previous question's controls from our footer.
        const buttons = dialog.querySelector('.h5p-dialog-inner .h5p-question-buttons')
          || footer?.querySelector('.h5p-question-buttons');
        if (!buttons) return;
        if (!footer) {
          footer = doc.createElement('div');
          footer.className = 'lesson-question-actions';
          dialog.append(footer);
        }
        if (buttons.parentElement !== footer) {
          footer.replaceChildren(buttons);
          phases.delete(dialog);
        }
        const phase = buttons.textContent.trim();
        if (phases.get(dialog) !== phase) {
          phases.set(dialog, phase);
          doc.defaultView.requestAnimationFrame(() => {
            const inner = dialog.querySelector('.h5p-dialog-inner');
            if (inner) inner.scrollTop = buttons.querySelector('.h5p-question-check-answer:not([style*="display: none"])') ? 0 : inner.scrollHeight;
          });
        }
        const title = dialog.querySelector('.h5p-dialog-title');
        if (title && !title.textContent.trim()) title.textContent = 'Quick check';
      });
    }
    const observer = new doc.defaultView.MutationObserver(arrange);
    observer.observe(root, { childList: true, subtree: true });
    arrange();
    return () => observer.disconnect();
  }
};
