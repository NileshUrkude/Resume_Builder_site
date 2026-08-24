"""Single source of truth for resume template metadata."""

TEMPLATE_MAP = {
    't1': 'resumes/t1.html',
    't1s': 'resumes/t1s.html',
    't2s': 'resumes/t2s.html',
    't3s': 'resumes/t3s.html',
    't4s': 'resumes/t4s.html',
    't5s': 'resumes/t5s.html',
}

VALID_TEMPLATES = frozenset(TEMPLATE_MAP.keys())
SINGLE_PAGE_TEMPLATES = VALID_TEMPLATES

TEMPLATE_LABELS = {
    't1': 'Executive Navy',
    't1s': 'Ocean Teal',
    't2s': 'Plum Sidebar',
    't3s': 'Crimson Pro',
    't4s': 'Slate & Sky',
    't5s': 'Compact One Page',
}

TEMPLATE_BLURBS = {
    't1': 'Navy & gold executive style — centered header, classic rules.',
    't1s': 'Teal minimal stack — clean sections with mint accents.',
    't2s': 'Purple sidebar — contact & skills on a colored panel.',
    't3s': 'Crimson timeline — red stripe with dense two columns.',
    't4s': 'Dark slate header — sky-blue highlights, modern grid.',
    't5s': 'Dense A4 layout — fits more content on a single page.',
}

TEMPLATE_FORM_LABELS = {
    't1': 'Executive Navy — gold & navy classic',
    't1s': 'Ocean Teal — mint minimal stack',
    't2s': 'Plum Sidebar — purple panel layout',
    't3s': 'Crimson Pro — red timeline columns',
    't4s': 'Slate & Sky — dark header modern',
    't5s': 'Compact One Page — dense two-column A4',
}

TEMPLATE_CHOICES = [(tid, TEMPLATE_LABELS[tid]) for tid in TEMPLATE_MAP]

# Fixed palette per template — each design looks distinct regardless of user accent pick.
TEMPLATE_THEMES = {
    't1': {
        'primary': '#1e3a5f',
        'accent': '#c9a227',
        'text': '#1e293b',
        'muted': '#64748b',
        'light': '#faf8f5',
        'pill_bg': '#eef2f7',
        'pill_border': '#cbd5e1',
        'header_bg': '#1e3a5f',
        'header_text': '#ffffff',
    },
    't1s': {
        'primary': '#0f766e',
        'accent': '#14b8a6',
        'text': '#134e4a',
        'muted': '#5eead4',
        'light': '#f0fdfa',
        'pill_bg': '#ccfbf1',
        'pill_border': '#99f6e4',
        'header_bg': '#0f766e',
        'header_text': '#ffffff',
    },
    't2s': {
        'primary': '#5b21b6',
        'accent': '#a78bfa',
        'text': '#1e1b4b',
        'muted': '#6b7280',
        'light': '#faf5ff',
        'pill_bg': '#ede9fe',
        'pill_border': '#c4b5fd',
        'sidebar_bg': '#4c1d95',
        'sidebar_text': '#f5f3ff',
    },
    't3s': {
        'primary': '#b91c1c',
        'accent': '#ef4444',
        'text': '#1f2937',
        'muted': '#6b7280',
        'light': '#fef2f2',
        'pill_bg': '#fee2e2',
        'pill_border': '#fecaca',
        'stripe': '#dc2626',
    },
    't4s': {
        'primary': '#0f172a',
        'accent': '#0ea5e9',
        'text': '#334155',
        'muted': '#64748b',
        'light': '#f0f9ff',
        'pill_bg': '#e0f2fe',
        'pill_border': '#7dd3fc',
        'header_bg': '#0f172a',
        'header_text': '#ffffff',
    },
    't5s': {
        'primary': '#14532d',
        'accent': '#22c55e',
        'text': '#1e293b',
        'muted': '#64748b',
        'light': '#f0fdf4',
        'pill_bg': '#dcfce7',
        'pill_border': '#86efac',
        'sidebar_bg': '#166534',
        'sidebar_text': '#f0fdf4',
        'header_bg': '#14532d',
        'header_text': '#ffffff',
    },
}
