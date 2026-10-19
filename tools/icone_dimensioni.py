# -*- coding: utf-8 -*-
"""Dieci icone a tratto singolo per «Le dimensioni» della home.

Stile unico: viewBox 48×48, tratto 1.4, colore corrente (ereditato dal CSS),
estremità arrotondate, niente riempimenti. Ogni icona è un piccolo oggetto
inciso, nello spirito delle tavole del pianeta.
"""

_A = 'xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"'

ICONE = {
    # libro aperto con pagine
    'edizioni': f'<svg {_A}><path d="M24 14c-4-3-10-4-16-3v24c6-1 12 0 16 3 4-3 10-4 16-3V11c-6-1-12 0-16 3z"/><path d="M24 14v24"/><path d="M12 18c3-.3 6 0 9 1M12 23c3-.3 6 0 9 1M27 19c3-1 6-1.3 9-1M27 24c3-1 6-1.3 9-1"/></svg>',
    # porta di libreria con scaffali
    'librerie': f'<svg {_A}><path d="M9 40V12a3 3 0 0 1 3-3h24a3 3 0 0 1 3 3v28"/><path d="M6 40h36"/><path d="M14 16h6v8h-6zM22 16h5v8h-5zM29 16h5v8h-5zM14 28h5v8h-5zM21 28h7v8h-7zM30 28h4v8h-4z"/></svg>',
    # microfono
    'podcast': f'<svg {_A}><rect x="18" y="8" width="12" height="20" rx="6"/><path d="M12 24a12 12 0 0 0 24 0"/><path d="M24 36v6M18 42h12"/><path d="M22 14h4M22 18h4M22 22h4"/></svg>',
    # palco in piazza: tenda e due figure
    'eventi': f'<svg {_A}><path d="M8 18h32l-3-7H11z"/><path d="M8 18v22M40 18v22"/><path d="M6 40h36"/><circle cx="19" cy="26" r="2.5"/><circle cx="29" cy="26" r="2.5"/><path d="M14 36c0-4 2-6 5-6s5 2 5 6M24 36c0-4 2-6 5-6s5 2 5 6"/></svg>',
    # leggio con foglio
    'formazione': f'<svg {_A}><path d="M14 16l20-5v16l-20 5z"/><path d="M24 32v10M18 42h12"/><path d="M18 20l12-3M18 24l12-3M18 28l8-2"/></svg>',
    # lente con costellazione
    'ricerca': f'<svg {_A}><circle cx="21" cy="21" r="12"/><path d="M30 30l10 10"/><circle cx="16" cy="19" r="1.2"/><circle cx="23" cy="15" r="1.2"/><circle cx="26" cy="24" r="1.2"/><path d="M16 19l7-4 3 9-10-5z"/></svg>',
    # giornale piegato
    'press': f'<svg {_A}><path d="M10 10h28v26a4 4 0 0 1-4 4H10z"/><path d="M10 40a4 4 0 0 1-4-4V18h4"/><path d="M15 16h10v8H15zM29 16h5M29 20h5M29 24h5M15 29h19M15 33h19"/></svg>',
    # pianeta con anello
    'progetto': f'<svg {_A}><circle cx="24" cy="24" r="10"/><path d="M8 20c-3 3 4 9 14 11s20 1 18-4c-1-2-4-3-8-4"/><path d="M19 17c2 2 5 3 8 2M17 25c1 3 4 5 8 5"/></svg>',
    # lettera che si apre
    'tlonletter': f'<svg {_A}><path d="M8 20l16-11 16 11v18a2 2 0 0 1-2 2H10a2 2 0 0 1-2-2z"/><path d="M8 20l16 11 16-11"/><path d="M8 38l12-10M40 38L28 28"/></svg>',
    # una tazza sul piattino, con il vapore
    'contatti': f'<svg {_A}><path d="M12 20h20v9a8 8 0 0 1-8 8h-4a8 8 0 0 1-8-8z"/><path d="M32 23h3a4 4 0 0 1 0 8h-3"/><path d="M8 42h32"/><path d="M18 15c0-2 2-2 2-4s-2-2-2-4M24 15c0-2 2-2 2-4s-2-2-2-4"/></svg>',
}
