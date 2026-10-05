"""Decode Ultra Sun/Ultra Moon branches for a separate gameplay audit."""
import json,re,struct,sys
from pathlib import Path
root=Path(__file__).parent;ref=root/'reference/pkhex'
sha=json.loads((ref/'tree.json').read_text())['sha']
gen6='--gen-six' in sys.argv
gen5='--gen-five' in sys.argv
gen4='--gen-four' in sys.argv
gen3='--gen-three' in sys.argv
gg='--lets-go' in sys.argv
gen2='--gen-two' in sys.argv
size=32 if gen2 else 28 if gen3 else 44 if gen4 else 60 if gen5 else 80 if gen6 else 84
code='gs' if gen2 else 'gg' if gg else 'rs' if gen3 else 'dp' if gen4 else 'bw' if gen5 else 'ao' if gen6 else 'uu'
table='g2' if gen2 else 'gg' if gg else 'g3' if gen3 else 'g4' if gen4 else 'g5' if gen5 else 'g6' if gen6 else 'uu'
types={int(n):name for name,n in re.findall(r'^\s*(\w+)\s*=\s*(\d+)\s*,',(ref/'PKHeX.Core/Legality/Evolutions/Methods/EvolutionType.cs').read_text(),re.M)}
raw=(ref/('PKHeX.Core/Resources/byte/personal/personal_'+code)).read_bytes();pairs={}
assert len(raw)%size==0
for sid in range(1,252 if gen2 else 810 if gg else 387 if gen3 else 494 if gen4 else 650 if gen5 else 722 if gen6 else 808):
 row=raw[sid*size:(sid+1)*size];pairs[sid]=(sid,0)
 first=0 if gen2 or gen3 or gen4 else struct.unpack_from('<H',row,28)[0]
 if first and not gen5:
  for form in range(1,row[32]):
   index=first+form-1
   assert index not in pairs
   pairs[index]=(sid,form)
p='PKHeX.Core/Resources/byte/evolve/evos_'+table+'.pkl';data=(ref/p).read_bytes()
n=struct.unpack_from('<H',data,2)[0];offsets=struct.unpack_from('<'+'H'*(n+1),data,4)
assert offsets[-1]==len(data)
records=[]
for slot,(a,b) in enumerate(zip(offsets,offsets[1:])):
 assert a<=b and (b-a)%8==0
 if a==b:continue
 sid,form=pairs[slot]
 for pos in range(a,b,8):
  block=data[pos:pos+8];arg,dest=struct.unpack_from('<HH',block,2)
  records.append({'gameTable':table,'sourceSpecies':sid,'sourceForm':form,'destinationSpecies':dest,'destinationForm':form if block[6]==255 else block[6],'evolutionType':types[block[0]],'argument':arg,'level':block[7],'source':'https://github.com/kwsch/PKHeX/blob/'+sha+'/'+p})
(root/('audit/gen-two-evolution-encounters.json' if gen2 else 'audit/lets-go-evolution-encounters.json' if gg else 'audit/gen-three-evolution-encounters.json' if gen3 else 'audit/gen-four-evolution-encounters.json' if gen4 else 'audit/gen-five-evolution-encounters.json' if gen5 else 'audit/gen-six-evolution-encounters.json' if gen6 else 'audit/older-evolution-encounters.json')).write_text(json.dumps(records,indent=2),encoding='utf-8')
print('Decoded',len(records),table,'evolution branches for gameplay review; not yet advertised as verified hunting routes')
