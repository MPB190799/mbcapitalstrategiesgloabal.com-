document.addEventListener("DOMContentLoaded", async () => {

    // Do not run on the glossary page itself
    if (window.location.pathname.startsWith('/pages/glossary')) return;

    // Only run on blog article pages
    if (!window.location.pathname.startsWith('/blog/')) return;

    // 1) Load glossary JSON
    let glossary = {};
    try {
        const res = await fetch("/pages/terms.json");
        glossary = await res.json();
    } catch (e) {
        console.error("Glossary could not be loaded:", e);
        return;
    }

    // 2) Find target content area
    const selectors = [
        ".article-body",
        ".blog-post-content",
        ".page-content",
        "main",
        ".post",
        ".content",
        ".container"
    ];

    let target = null;
    for (const s of selectors) {
        const el = document.querySelector(s);
        if (el) { target = el; break; }
    }
    if (!target) return;

    // 3) Link glossary terms — only inside text nodes, never inside attribute values,
    // <a>, <script>, <style>, <code>, <pre>, <button>, <h1>
    const walker = document.createTreeWalker(target, NodeFilter.SHOW_TEXT, {
        acceptNode(node) {
            let parent = node.parentElement;
            while (parent && parent !== target) {
                const tag = parent.tagName.toLowerCase();
                if (tag === 'a' || tag === 'script' || tag === 'style' ||
                    tag === 'code' || tag === 'pre' || tag === 'button' ||
                    tag === 'h1') {
                    return NodeFilter.FILTER_REJECT;
                }
                parent = parent.parentElement;
            }
            return NodeFilter.FILTER_ACCEPT;
        }
    });

    // Collect text nodes first (modifying during walk causes issues)
    const textNodes = [];
    let node;
    while (node = walker.nextNode()) textNodes.push(node);

    // Sort terms by length (longest first) to avoid partial matches
    const sortedTerms = Object.entries(glossary).sort((a, b) => b[0].length - a[0].length);

    // Track linked slugs to avoid duplicate links for same concept on the page
    const linkedSlugs = new Set();

    for (const textNode of textNodes) {
        const text = textNode.textContent;
        if (!text.trim()) continue;

        const matches = [];
        for (const [term, slug] of sortedTerms) {
            if (linkedSlugs.has(slug)) continue;
            const safeTerm = term.replace(/[-/\\^$*+?.()|[\]{}]/g, "\\$&");
            const regex = new RegExp(`\\b(${safeTerm})\\b`, "gi");
            const match = regex.exec(text);
            if (match) {
                const start = match.index;
                const end = start + match[0].length;
                const overlaps = matches.some(m => !(end <= m.start || start >= m.end));
                if (!overlaps) {
                    matches.push({ start, end, text: match[1], slug, term });
                }
            }
        }

        if (matches.length === 0) continue;

        matches.sort((a, b) => a.start - b.start);

        const fragment = document.createDocumentFragment();
        let lastIndex = 0;

        for (const m of matches) {
            if (m.start > lastIndex) {
                fragment.appendChild(document.createTextNode(text.slice(lastIndex, m.start)));
            }
            const link = document.createElement('a');
            link.href = `/pages/glossary.html?term=${m.slug}`;
            link.className = 'glossar-link';
            link.textContent = m.text;
            fragment.appendChild(link);
            lastIndex = m.end;
            linkedSlugs.add(m.slug);
        }

        if (lastIndex < text.length) {
            fragment.appendChild(document.createTextNode(text.slice(lastIndex)));
        }

        textNode.parentNode.replaceChild(fragment, textNode);
    }

});
