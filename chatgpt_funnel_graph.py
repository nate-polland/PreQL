import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from collections import defaultdict

TOTAL_SESSIONS = 235

# Transition data from BigQuery (users >= 3, Mar 8-10)
transitions_raw = [
    ("seamless-registration\nphoneInfoContinue",         "seamless-registration\nphoneInfoContinue",         219),
    ("seamless-registration\nphoneInfoContinue",          "seamless-registration\nphoneVerificationContinue", 211),
    ("seamless-registration\nphoneVerificationContinue",  "seamless-registration\nphoneVerificationContinue", 163),
    ("link-chatgpt\nnavDestination",                      "link-chatgpt\nagreeClick",                         140),
    ("seamless-registration\nphoneVerificationContinue",  "link-chatgpt\nnavDestination",                     107),
    ("login-web-redirect\nredirectToLogin",               "login-unknown\ngetLoginHelp",                       61),
    ("seamless-registration\nshortPersonalInfo",          "seamless-registration\nshortPersonalInfoContinue",  47),
    ("seamless-registration\nphoneVerificationContinue",  "seamless-registration\nshortPersonalInfo",          45),
    ("seamless-registration\nshortPersonalInfoContinue",  "seamless-registration\nshortPersonalInfoContinue",  44),
    ("link-mcp-twofa-enrolled\nnavDestination",           "link-mcp-twofa-enrolled\ncontinueClick",            37),
    ("seamless-registration\nphoneVerificationContinue",  "link-mcp-twofa-enrolled\nnavDestination",           37),
    ("link-mcp-twofa-enrolled\ncontinueClick",            "login-web-redirect\nredirectToLogin",               36),
    ("login-unknown\ngetLoginHelp",                       "login\ninvalidCredentials",                         27),
    ("seamless-registration\nshortPersonalInfoContinue",  "login-web-redirect\nredirectToLogin",               23),
    ("seamless-registration\nshortPersonalInfoContinue",  "seamless-registration\nshortDobValidationError",    21),
    ("ump-enter-otc\nverifyCode",                         "link-chatgpt\nnavDestination",                      20),
    ("login-unknown\ngetLoginHelp",                       "login-unknown-password-disabled-text\nloginClick",  19),
    ("login-unknown-password-disabled-text\nloginClick",  "ump-phone-verify\nmemberSupport",                   13),
    ("ump-phone-verify\nverifyPhone",                     "ump-enter-otc\nverifyCode",                         18),
    ("force-2fa-phone-check\nnavDestination",             "force-2fa-sending-phone-otc\nnavDestination",       15),
    ("force-2fa-sending-phone-otc\nnavDestination",       "force-2fa-verify-phone-otc\nsubmitClick",           10),
    ("force-2fa-verify-phone-otc\nsubmitClick",           "link-chatgpt\nnavDestination",                       9),
    ("login\ninvalidCredentials",                         "login-unknown-step-1-dup\nclickContinue",           17),
    ("login-unknown-step-1-dup\nclickContinue",           "login-unknown-step-1-dup\ngetLoginHelp",            19),
    ("login-web-redirect\nredirectToLogin",               "login-password-options\ntextCode",                  10),
    ("seamless-registration\nphoneVerificationContinue",  "force-2fa-phone-check\nnavDestination",              8),
    ("login-unknown\ngetLoginHelp",                       "login\nemailValidation",                            15),
    ("login\nemailValidation",                            "login-unknown-password-disabled-text\nloginClick",   9),
    ("seamless-registration\nmatchFailedReturn",          "reg-step-1\nnavDestination",                         8),
    ("login-unknown-password-disabled-text\nloginClick",  "seamless-registration\nphoneInfoContinue",           8),
    ("login-password-options\nsubmitClick",               "seamless-registration\nphoneInfoContinue",           8),
]

# Remove self-loops for graph edges
transitions = [(f, t, w) for f, t, w in transitions_raw if f != t]

# Build directed graph
G = nx.DiGraph()
for f, t, w in transitions:
    if G.has_edge(f, t):
        G[f][t]['weight'] += w
    else:
        G.add_edge(f, t, weight=w)

# Compute drop-off per node:
# users_in = max of incoming edge weights (or TOTAL_SESSIONS for entry node)
# users_out = sum of outgoing edge weights
# dropped = users_in - users_out
ENTRY = "seamless-registration\nphoneInfoContinue"
node_in = defaultdict(int)
node_out = defaultdict(int)
node_in[ENTRY] = TOTAL_SESSIONS

for f, t, w in transitions:
    node_out[f] += w
    node_in[t] = max(node_in[t], w)  # take max incoming path

# For well-connected nodes use sum of all incoming
node_in_sum = defaultdict(int)
for f, t, w in transitions:
    node_in_sum[t] += w
node_in_sum[ENTRY] = TOTAL_SESSIONS

dropoff = {}
for node in G.nodes():
    arrived = node_in_sum[node]
    continued = node_out[node]
    dropped = max(0, arrived - continued)
    if arrived > 0:
        dropoff[node] = (dropped, round(dropped * 100 / arrived))

# Node color coding
def get_color(node):
    screen = node.split('\n')[0]
    if screen == 'seamless-registration':   return '#4C9BE8'
    elif screen == 'link-chatgpt':          return '#2ECC71'
    elif screen == 'link-mcp-twofa-enrolled': return '#9B59B6'
    elif screen in ('ump-phone-verify', 'ump-enter-otc'): return '#E67E22'
    elif 'force-2fa' in screen:             return '#E74C3C'
    elif 'login' in screen:                 return '#F39C12'
    elif screen == 'reg-step-1':            return '#95A5A6'
    else:                                   return '#BDC3C7'

# Layout
pos = {
    # Entry
    "seamless-registration\nphoneInfoContinue":          (0,    10),
    "seamless-registration\nphoneVerificationContinue":  (0,     8),
    "seamless-registration\nshortPersonalInfo":          (-3,    6),
    "seamless-registration\nshortPersonalInfoContinue":  (-3,   4.5),
    "seamless-registration\nshortDobValidationError":    (-5,   3.5),
    "seamless-registration\nmatchFailedReturn":          (-5,    2),
    # 2FA enrollment
    "link-mcp-twofa-enrolled\nnavDestination":           (3.5,   6),
    "link-mcp-twofa-enrolled\ncontinueClick":            (3.5,  4.5),
    # Force 2FA — spread out vertically to avoid overlap
    "force-2fa-phone-check\nnavDestination":             (-7,    7),
    "force-2fa-sending-phone-otc\nnavDestination":       (-7,   5.5),
    "force-2fa-verify-phone-otc\nsubmitClick":           (-7,    4),
    # Fallback — moved closer
    "reg-step-1\nnavDestination":                        (-6.5,  1),
    # Login redirect
    "login-web-redirect\nredirectToLogin":               (0,     3),
    "login-unknown\ngetLoginHelp":                       (0,    1.5),
    "login\ninvalidCredentials":                         (-3,    0),
    "login\nemailValidation":                            (3,     0),
    "login-unknown-step-1-dup\nclickContinue":           (-3,  -1.5),
    "login-unknown-step-1-dup\ngetLoginHelp":            (-3,   -3),
    "login-unknown-password-disabled-text\nloginClick":  (3,   -1.5),
    "login-password-options\ntextCode":                  (5.5,  1.5),
    "login-password-options\nsubmitClick":               (5.5,   0),
    # Phone verify
    "ump-phone-verify\nmemberSupport":                   (5.5, -1.5),
    "ump-phone-verify\nverifyPhone":                     (5.5,  -3),
    "ump-enter-otc\nverifyCode":                         (5.5, -4.5),
    # Success
    "link-chatgpt\nnavDestination":                      (0,    -5),
    "link-chatgpt\nagreeClick":                          (0,   -6.5),
}

# Any unplaced nodes
placed_x = 8
for node in G.nodes():
    if node not in pos:
        pos[node] = (placed_x, -2)
        placed_x += 1.5

# Draw
node_colors  = [get_color(n) for n in G.nodes()]
edge_weights = [G[u][v]['weight'] for u, v in G.edges()]
max_w        = max(edge_weights) if edge_weights else 1
edge_widths  = [0.8 + 5 * (w / max_w) for w in edge_weights]
edge_labels  = {(u, v): str(G[u][v]['weight']) for u, v in G.edges() if G[u][v]['weight'] >= 10}

fig, ax = plt.subplots(figsize=(28, 24))
ax.set_facecolor('#F0F2F5')
fig.patch.set_facecolor('#F0F2F5')

nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=3000, alpha=0.95, ax=ax,
                       linewidths=2, edgecolors='white')

# Node labels (screen + event) below each node
for node, (x, y) in pos.items():
    if node not in G.nodes():
        continue
    parts  = node.split('\n')
    screen = parts[0]
    event  = parts[1] if len(parts) > 1 else ''
    label  = f"{screen}\n{event}" if event else screen
    ax.text(x, y - 0.52, label, ha='center', va='top',
            fontsize=7.5, fontweight='bold', color='#222222',
            bbox=dict(boxstyle='round,pad=0.25', fc='white', ec='#cccccc', alpha=0.88))

# Drop-off annotations — shown in red above each node (skip entry and terminal success)
TERMINAL = {"link-chatgpt\nagreeClick", "reg-step-1\nnavDestination",
            "login-unknown-step-1-dup\ngetLoginHelp"}
for node, (x, y) in pos.items():
    if node not in G.nodes() or node == ENTRY or node in TERMINAL:
        continue
    if node in dropoff:
        dropped, pct = dropoff[node]
        if dropped > 0 and pct > 0:
            ax.text(x, y + 0.48, f"↓ {dropped} dropped ({pct}%)",
                    ha='center', va='bottom', fontsize=7, color='#C0392B', fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.2', fc='#FDECEA', ec='#E74C3C', alpha=0.9))

nx.draw_networkx_edges(G, pos, width=edge_widths, alpha=0.5, edge_color='#444444',
                       arrows=True, arrowsize=18, arrowstyle='-|>',
                       connectionstyle='arc3,rad=0.08', ax=ax,
                       min_source_margin=28, min_target_margin=28)

nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8,
                              bbox=dict(boxstyle='round,pad=0.25', fc='white', ec='#cccccc', alpha=0.9),
                              ax=ax)

legend_items = [
    mpatches.Patch(color='#4C9BE8', label='seamless-registration (entry)'),
    mpatches.Patch(color='#2ECC71', label='link-chatgpt (success ✓)'),
    mpatches.Patch(color='#9B59B6', label='link-mcp-twofa-enrolled'),
    mpatches.Patch(color='#E67E22', label='ump phone verify'),
    mpatches.Patch(color='#E74C3C', label='force-2fa'),
    mpatches.Patch(color='#F39C12', label='login screens'),
    mpatches.Patch(color='#95A5A6', label='reg-step-1 (fallback)'),
    mpatches.Patch(color='#FDECEA', label='↓ drop-off annotation'),
]
ax.legend(handles=legend_items, loc='upper right', fontsize=10,
          framealpha=0.9, edgecolor='#cccccc', fancybox=True)
ax.set_title('ChatGPT Auth Funnel — Screen+Event Transitions\n'
             'Mar 8–10 2026  |  n=235 sessions  |  Edge labels = user count (≥10)  |  Red = drop-off',
             fontsize=14, fontweight='bold', pad=20, color='#222222')
ax.axis('off')

plt.tight_layout()
output_path = '/Users/npolland/Documents/Claude Code/Text-to-SQL/chatgpt_funnel_graph.png'
plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
print(f"Saved to {output_path}")
