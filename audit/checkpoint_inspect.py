import pathlib, hashlib, torch, json, sys
ckpt_path = r'D:\NEUROFRAME X\weights\epic\tsm_rgb.ckpt'
# Compute SHA256
p = pathlib.Path(ckpt_path)
sha256 = hashlib.sha256()
with p.open('rb') as f:
    for chunk in iter(lambda: f.read(8192), b''):
        sha256.update(chunk)
print('SHA256:', sha256.hexdigest())
# Load checkpoint
try:
    state = torch.load(str(p), map_location='cpu')
except Exception as e:
    print('Error loading checkpoint:', e)
    sys.exit(1)
print('Checkpoint type:', type(state))
if isinstance(state, dict):
    keys = list(state.keys())
    print('Top-level keys (sample):', keys[:10], '... total', len(keys))
    if 'state_dict' in state:
        sd = state['state_dict']
        sd_keys = list(sd.keys())
        print('state_dict keys sample:', sd_keys[:20])
        heads = [k for k in sd_keys if ('fc_' in k or 'head' in k.lower())]
        print('Potential head keys:', heads[:20])
    else:
        # maybe model directly stored
        sd_keys = list(state.keys())
        heads = [k for k in sd_keys if ('fc_' in k or 'head' in k.lower())]
        print('Potential head keys (no state_dict):', heads[:20])
else:
    print('Checkpoint is not a dict')
