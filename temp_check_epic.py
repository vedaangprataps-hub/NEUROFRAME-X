import os, torch, json
ckpt_path = r'D:\\NEUROFRAME X\\weights\\epic\\tsm_rgb.ckpt'
print('Exists?', os.path.isfile(ckpt_path))
state = torch.load(ckpt_path, map_location='cpu')
if isinstance(state, dict) and 'state_dict' in state:
    sd = state['state_dict']
else:
    sd = state
print('Num keys:', len(sd))
print('Sample keys:', list(sd.keys())[:10])
verb_keys = [k for k in sd if 'fc_verb' in k]
noun_keys = [k for k in sd if 'fc_noun' in k]
print('Verb head keys count', len(verb_keys))
print('Noun head keys count', len(noun_keys))
# Check classification head dimensions if present
if verb_keys:
    verb_weight = sd[verb_keys[0]]
    print('Verb weight shape', verb_weight.shape)
if noun_keys:
    noun_weight = sd[noun_keys[0]]
    print('Noun weight shape', noun_weight.shape)
