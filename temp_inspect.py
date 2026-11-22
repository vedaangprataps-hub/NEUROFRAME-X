import os, torch, json
ckpt_path = r'D:\\NEUROFRAME X\\weights\\epic\\tsm_rgb.ckpt'
print('Exists?', os.path.isfile(ckpt_path))
state = torch.load(ckpt_path, map_location='cpu')
print('Checkpoint type:', type(state))
if isinstance(state, dict) and 'state_dict' in state:
    sd = state['state_dict']
else:
    sd = state
print('Number of keys:', len(sd))
# Sample keys
print('Sample keys:', list(sd.keys())[:10])
# Find classification layer weight shape
for k, v in sd.items():
    if 'weight' in k.lower() and v.dim()==2:
        print('Classification weight key:', k, 'shape', v.shape)
        break
# Check for verb/noun heads
verb_heads = [k for k in sd if 'fc_verb' in k]
noun_heads = [k for k in sd if 'fc_noun' in k]
print('Verb heads count:', len(verb_heads))
print('Noun heads count:', len(noun_heads))
