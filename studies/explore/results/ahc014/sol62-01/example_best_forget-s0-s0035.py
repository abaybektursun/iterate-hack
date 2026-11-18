import sys
import time
import random
import math
from heapq import heappush, heappop


def main():
    start = time.perf_counter()
    deadline = start + 2.89
    data = list(map(int, sys.stdin.buffer.read().split()))
    if not data:
        return
    n, m = data[:2]
    mid = n // 2
    scale = mid * mid
    sparse = m < 0.046*n*n
    stride = 1 << (2*n-1).bit_length()
    origin = n*stride
    size = 3*n*stride
    steps = (stride, 1, stride+1, stride-1)
    nl = 6*n-2
    offsets = [0]*nl
    line_steps = [stride]*n+[1]*n+[stride+1]*(2*n-1)+[stride-1]*(2*n-1)
    axes = [0]*(2*n)+[2]*(4*n-2)
    info = [None]*size
    xs, ys, weight = [0]*size, [0]*size, [0]*size
    blank = bytearray(b'\2')*size
    powers = [1 << (2*i) for i in range(n)]
    evens = sum(powers)
    odds = evens << 1
    masks = [[0]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1,n):
            masks[i][j] = masks[j][i] = powers[j]-2*powers[i]
    coords = []
    for x in range(n):
        for y in range(n):
            p = origin+x*stride+y
            coords.append(p)
            blank[p] = 0
            xs[p],ys[p] = x,y
            weight[p] = (x-mid)**2+(y-mid)**2+1
            ip = ((y,powers[x],x),(n+x,powers[y],y),
                  (3*n-1+y-x,powers[x],x),(4*n-1+x+y,powers[x],x))
            info[p] = ip
            for ax,(line,bit,t) in enumerate(ip):
                offsets[line] = p-t*steps[ax]
    initial = [origin+x*stride+y for x,y in zip(data[2::2],data[3::2])]
    init_board = [0]*nl
    for p in initial:
        blank[p] = 1
        for line,bit,t in info[p]:
            init_board[line] |= bit
    rng = random.Random(201893+n*2357+m)
    rand, rr = rng.random, rng.randrange
    prizes = [[1/(1+0.20*i*w/scale) for w in range(2*scale+2)] for i in range(38)]
    fronts = []
    for dx,dy in ((1,0),(0,1),(-1,0),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
        f = [1.0]*size
        for p in coords:
            t = (dx*(xs[p]-mid)+dy*(ys[p]-mid))/mid
            f[p] = 1/(1+1.1*max(0,t-0.21))
        fronts.append(f)
    sides = (5,7,9,11)

    def flip(op,board,occ):
        a = op[1]
        occ[a] ^= 1
        for line,bit,_ in info[a]:
            board[line] ^= bit
        board[op[5]] ^= op[6]&odds
        board[op[7]] ^= op[8]&odds
        board[op[9]] ^= op[10]&odds
        board[op[11]] ^= op[12]&odds

    def legal(op,board,occ):
        _,a,b,c,d,l0,s0,l1,s1,l2,s2,l3,s3 = op
        return (not occ[a] and occ[b] == 1 and occ[c] == 1 and occ[d] == 1 and
                not (board[l0]&s0 or board[l1]&s1 or board[l2]&s2 or board[l3]&s3))

    def grow(ops,board,occ,value,style,tabu,before,recover,retention):
        bias,noise,skew,outward,diag,power,front,link,expand = style
        prize = prizes[bias]
        direction = fronts[front] if front >= 0 else None
        heap = []
        pending = {}
        if recover:
            for op in recover:
                a,b,c,d = op[1:5]
                if occ[a] or a in tabu:
                    continue
                for q in (b,c,d):
                    if not occ[q]:
                        pending.setdefault(q,[]).append(op)

        def near(p,ax):
            line,bit,t = info[p][ax]
            v = board[line]
            k = (v&(bit-1)).bit_length()-1
            st = steps[ax]
            lo = 0 if k&1 else p+((k>>1)-t)*st
            hi = v&-(bit<<1)
            if hi:
                k = (hi&-hi).bit_length()-1
                if not k&1:
                    return lo,p+((k>>1)-t)*st
            return lo,0

        def priority(a,b,c,d,ax,u,v,ia):
            cost = u+v+skew*abs(u-v)
            if power != 1:
                cost = cost**power
            if ax:
                cost *= diag
            w = weight[a]
            key = cost*prize[w]*(1+noise*rand())
            if w > weight[b] and w > weight[c] and w > weight[d]:
                key *= outward
            if direction is not None:
                key *= direction[a]
            if expand and ax:
                key *= 1-expand*((not (board[ia[0][0]]&evens))+
                                 (not (board[ia[1][0]]&evens)))
            if link:
                r = ax^2
                p0,p1 = near(a,r)
                if p0 or p1:
                    q0,q1 = near(a,r+1)
                    if q0 or q1:
                        key *= 1-link
            if tabu:
                key *= tabu.get(a,1)
            return key

        def rescue(op):
            if not legal(op,board,occ):
                return
            _,a,b,c,d = op[:5]
            ax = 0 if op[5]<2*n else 2
            ia = info[a]
            u = abs(info[b][ax][2]-info[c][ax][2])
            v = abs(info[d][ax+1][2]-info[c][ax+1][2])
            key = priority(a,b,c,d,ax,u,v,ia)*retention
            heappush(heap,(key,)+op[1:])

        def offer(b,c,d,ax):
            a = b+d-c
            if occ[a]:
                return
            ay = ax+1
            ia,ib,ic,id_ = info[a],info[b],info[c],info[d]
            l0,_,at = ia[ax]
            l1,_,au = ia[ay]
            s0 = masks[at][id_[ax][2]]
            s1 = masks[au][ib[ay][2]]
            if board[l0]&s0 or board[l1]&s1:
                return
            l2,_,ct = ic[ax]
            l3,_,cu = ic[ay]
            bt,du = ib[ax][2],id_[ay][2]
            s2,s3 = masks[bt][ct],masks[du][cu]
            key = priority(a,b,c,d,ax,abs(bt-ct),abs(du-cu),ia)
            heappush(heap,(key,a,b,c,d,l0,s0,l1,s1,l2,s2,l3,s3))

        def discover(p,ax,ends):
            ay = ax+1
            b0,b1 = near(p,ax)
            d0,d1 = near(p,ay)
            if b0:
                if d0:
                    offer(b0,p,d0,ax)
                if d1:
                    offer(b0,p,d1,ax)
            if b1:
                if d0:
                    offer(b1,p,d0,ax)
                if d1:
                    offer(b1,p,d1,ax)
            if not ends:
                return
            if b0:
                q0,q1 = near(b0,ay)
                if q0:
                    offer(p,b0,q0,ax)
                if q1:
                    offer(p,b0,q1,ax)
            if b1:
                q0,q1 = near(b1,ay)
                if q0:
                    offer(p,b1,q0,ax)
                if q1:
                    offer(p,b1,q1,ax)
            if d0:
                q0,q1 = near(d0,ax)
                if q0:
                    offer(q0,d0,p,ax)
                if q1:
                    offer(q1,d0,p,ax)
            if d1:
                q0,q1 = near(d1,ax)
                if q0:
                    offer(q0,d1,p,ax)
                if q1:
                    offer(q1,d1,p,ax)

        changed = []
        work = 0
        if before is not None:
            for l,v in enumerate(board):
                if v != before[l]:
                    pts = v&evens
                    if pts:
                        work += pts.bit_count()
                        changed.append((l,pts))
        if before is None or work > m+len(ops):
            for p in initial:
                discover(p,0,False)
                discover(p,2,False)
            for op in ops:
                p = op[1]
                discover(p,0,False)
                discover(p,2,False)
        else:
            visited = set()
            for l,pts in changed:
                off,st,ax = offsets[l],line_steps[l],axes[l]
                while pts:
                    bit = pts&-pts
                    pts ^= bit
                    p = off+((bit.bit_length()-1)>>1)*st
                    tag = (p<<2)+ax
                    if tag not in visited:
                        visited.add(tag)
                        discover(p,ax,True)
        if recover:
            for op in recover:
                if op[1] not in tabu:
                    rescue(op)
        ticks = 0
        while heap:
            op = heappop(heap)
            _,a,b,c,d,l0,s0,l1,s1,l2,s2,l3,s3 = op
            if occ[a] or board[l0]&s0 or board[l1]&s1 or board[l2]&s2 or board[l3]&s3:
                continue
            flip(op,board,occ)
            ops.append(op)
            value += weight[a]
            discover(a,0,True)
            discover(a,2,True)
            if a in pending:
                for other in pending.pop(a):
                    rescue(other)
            ticks += 1
            if ticks&15 == 0 and time.perf_counter() >= deadline:
                break
        return value,ops,board,occ

    cache = {}

    def indices(old):
        cached = cache.get(id(old))
        if cached is not None:
            return cached[1:]
        owners = [[] for _ in range(nl)]
        depend, pos = {}, {}
        for i,op in enumerate(old):
            flag = 1 << i
            a = op[1]
            depend[a] = pos[a] = flag
            for j in sides:
                owners[op[j]].append((op[j+1]&odds,a))
        for op in reversed(old):
            flag = depend[op[1]]
            for p in op[2:5]:
                if not blank[p]:
                    depend[p] |= flag
        if len(cache)>=22:
            cache.pop(next(iter(cache)))
        cache[id(old)] = old,owners,depend,pos
        return owners,depend,pos

    def conflict(op,board,owners,depend,limit):
        cut = depend.get(op[1],0)
        for j in sides:
            line,span = op[j],op[j+1]
            hit = board[line]&span
            if not hit:
                continue
            dots,edges = hit&evens,hit&odds
            if dots:
                off,st = offsets[line],line_steps[line]
                while dots:
                    bit = dots&-dots
                    dots ^= bit
                    p = off+((bit.bit_length()-1)>>1)*st
                    dep = depend.get(p,0)
                    if not dep:
                        return -1
                    cut |= dep
            if edges:
                for span,p in owners[line]:
                    if span&edges:
                        cut |= depend[p]
            if cut.bit_count()>limit:
                return -1
        return cut

    def mask_loss(old,cut):
        loss = 0
        while cut:
            bit = cut&-cut
            cut ^= bit
            loss += weight[old[bit.bit_length()-1][1]]
        return loss

    def directed(old,board,occ,donor):
        owners,depend,pos = indices(old)
        limit = max(8,int(0.34*len(old)))

        if donor is not None:
            donorops = donor[1]
            diff = [op for op in donorops if not occ[op[1]]]
            if diff:
                lookup = {op[1]:op for op in donorops}
                order = {op[1]:i for i,op in enumerate(donorops)}
                answer = None
                bestkey = float('inf')
                for target in rng.sample(diff,min(7,len(diff))):
                    keep = {}
                    todo = [target]
                    while todo and len(keep)<11:
                        op = todo.pop()
                        p = op[1]
                        if p not in keep:
                            keep[p] = op
                            todo.extend(lookup[q] for q in op[2:5] if not occ[q] and q not in keep)
                    if todo:
                        continue
                    cut = req = reward = 0
                    for op in keep.values():
                        part = conflict(op,board,owners,depend,limit)
                        if part < 0:
                            cut = -1
                            break
                        cut |= part
                        reward += weight[op[1]]
                        for q in op[2:5]:
                            req |= pos.get(q,0)
                    if cut <= 0 or cut&req or cut.bit_count()>limit:
                        continue
                    loss = mask_loss(old,cut)
                    key = (loss+0.065*scale*cut.bit_count())/(reward+0.13*scale)
                    key *= 0.77+0.46*rand()
                    if key<bestkey:
                        bestkey = key
                        answer = (sorted(keep.values(),key=lambda op:order[op[1]]),cut,loss)
                if answer is not None:
                    return answer

        dots = [v&evens for v in board]
        far = rand()<0.38
        redraw = rand()<0.32
        broad = rand()<0.18
        seen = set()
        choices = []
        bias = (3.6 if broad else 2.15)/scale

        def neighbors(p,ax,line,bit,t):
            row = dots[line]
            lo,hi = row&(bit-1),row&-(bit<<1)
            out = []
            st = steps[ax]
            if lo:
                z = (lo.bit_length()-1)>>1
                q = p+(z-t)*st
                out.append((q,masks[z][t],t-z,0))
                if far and not blank[q]:
                    lo ^= powers[z]
                    if lo:
                        z = (lo.bit_length()-1)>>1
                        out.append((p+(z-t)*st,masks[z][t],t-z,q))
            if hi:
                b = hi&-hi
                z = (b.bit_length()-1)>>1
                q = p+(z-t)*st
                out.append((q,masks[z][t],z-t,0))
                if far and not blank[q]:
                    hi ^= b
                    if hi:
                        z = ((hi&-hi).bit_length()-1)>>1
                        out.append((p+(z-t)*st,masks[z][t],z-t,q))
            return out

        for _ in range(29 if broad else (15 if far else 19)):
            idx = rr(m+len(old)) if rand()<0.78 else m+rr(len(old))
            c = initial[idx] if idx<m else old[idx-m][1]
            ic = info[c]
            for ax in (0,2):
                ay = ax+1
                l2,bit,ct = ic[ax]
                bs = neighbors(c,ax,l2,bit,ct)
                if not bs:
                    continue
                l3,bit,cu = ic[ay]
                ds = neighbors(c,ay,l3,bit,cu)
                for b,s2,u,bblock in bs:
                    l1,_,bt = info[b][ay]
                    for d,s3,v,dblock in ds:
                        if bblock and dblock:
                            continue
                        a = b+d-c
                        fill = occ[a]
                        if fill and (fill==2 or not redraw or blank[a]):
                            continue
                        sig = (a,c,ax)
                        if sig in seen:
                            continue
                        l0,_,dt = info[d][ax]
                        ia = info[a]
                        s0 = masks[ia[ax][2]][dt]
                        s1 = masks[ia[ay][2]][bt]
                        db0,db1 = dots[l0]&s0,dots[l1]&s1
                        if db0 and db1:
                            continue
                        db = db0 or db1
                        block = bblock or dblock
                        if db:
                            if block or db&(db-1):
                                continue
                            line = l0 if db0 else l1
                            block = offsets[line]+((db.bit_length()-1)>>1)*line_steps[line]
                            if blank[block]:
                                continue
                        ec = (bool(board[l0]&s0&odds)+bool(board[l1]&s1&odds)+
                              bool(board[l2]&s2&odds)+bool(board[l3]&s3&odds))
                        if not (fill or ec or block) or (fill and ec==4):
                            continue
                        seen.add(sig)
                        w = weight[a]
                        gain = 1+w*bias
                        if w>weight[b] and w>weight[c] and w>weight[d]:
                            gain *= 1.25
                        key = (1+0.27*(u+v)+0.43*ec+0.47*bool(block))/gain
                        key *= (0.46+rand())*(1.14 if fill else 1)
                        choices.append((key,(0.0,a,b,c,d,l0,s0,l1,s1,l2,s2,l3,s3)))
        choices.sort()
        answer = None
        bestkey = float('inf')
        for key,target in choices[:(15 if broad else 10)]:
            cut = conflict(target,board,owners,depend,limit)
            if cut<=0:
                continue
            a,b,c,d = target[1:5]
            if cut&(pos.get(b,0)|pos.get(c,0)|pos.get(d,0)):
                continue
            loss = mask_loss(old,cut)
            adjust = loss-(weight[a] if occ[a] else 0)
            k = key*(1+0.10*cut.bit_count()+0.23*adjust/(weight[a]+0.10*scale))
            if k<bestkey:
                bestkey = k
                answer = ([target],cut,loss)
        return answer

    def replay(deleted,ops,board,occ,value):
        for op in deleted:
            if legal(op,board,occ):
                flip(op,board,occ)
                ops.append(op)
                value += weight[op[1]]
        return value

    def style(i,fresh):
        if i==0:
            return 8,0.22,0.10,0.86,1.02,1,-1,0,0
        front = rr(8) if rand()<(0.57 if fresh and sparse else 0.22) else -1
        link = 0.12+0.24*rand() if rand()<(0.43 if fresh else 0.25) else 0
        expand = 0.12+0.25*rand() if rand()<(0.58 if fresh and sparse else 0.16) else 0
        if fresh and sparse and rand()<0.46:
            return (rr(11,38),0.07+0.52*rand(),-0.18+0.38*rand(),
                    0.53+0.38*rand(),0.73+0.52*rand(),0.52+0.49*rand(),front,link,expand)
        if fresh:
            return (rr(29),0.08+0.84*rand(),-0.08+0.34*rand(),
                    0.65+0.34*rand(),0.81+0.48*rand(),
                    1 if rand()<0.81 else 0.68+0.57*rand(),front,link,expand)
        return (rr(31),0.13+1.06*rand(),-0.13+0.39*rand(),0.67+0.37*rand(),
                0.81+0.52*rand(),1 if rand()<0.85 else 0.69+0.56*rand(),front,link,expand)

    best = (0,[],init_board,blank)
    current = best
    elite = []
    lanes = []
    i = stagnation = 0
    while time.perf_counter()<deadline:
        elapsed = time.perf_counter()-start
        cooling = max(0,1-elapsed/2.89)
        fresh = i<5 or not current[1] or (
            elapsed<(0.64 if sparse else 0.49) and
            (i<13 or rand()<(0.58 if sparse else 0.42))
        ) or rand()<(0.045 if stagnation>100 else 0.018)
        before = None
        tabu = {}
        recover = ()
        retention = 1.0
        lane_idx = -1
        if fresh:
            board,occ = init_board[:],blank[:]
            ops = []
            value = 0
        else:
            r = rand()
            if r<0.20:
                base = best
            elif r<0.34 and elite:
                base = rng.choice(elite)
            elif r<(0.58 if elapsed<2.12 else 0.43) and lanes:
                lane_idx = min(rr(len(lanes)),rr(len(lanes)))
                base = lanes[lane_idx][2]
            else:
                base = current
            value,old,before,old_occ = base
            board,occ = before[:],old_occ[:]
            length = len(old)
            mode = rand()
            mutation = None
            if mode<0.43:
                donor = None
                if mode<0.09:
                    if lanes and rand()<0.76:
                        donor = rng.choice(lanes)[0]
                    elif elite:
                        donor = rng.choice(elite)
                mutation = directed(old,board,occ,donor)
            if mutation is not None:
                targets,bits,loss = mutation
                ops,deleted = [],[]
                last = 0
                while bits:
                    bit = bits&-bits
                    bits ^= bit
                    j = bit.bit_length()-1
                    ops.extend(old[last:j])
                    op = old[j]
                    flip(op,board,occ)
                    deleted.append(op)
                    last = j+1
                ops.extend(old[last:])
                value = replay(targets,ops,board,occ,value-loss)
                r = rand()
                if r<0.55:
                    value = replay(deleted,ops,board,occ,value)
                elif r<0.88:
                    recover = deleted
                    retention = 0.40+0.42*rand()
                else:
                    tabu = dict.fromkeys((op[1] for op in deleted),1.18+1.24*rand())
            elif mode>0.90:
                cut = int(length*(0.23+0.76*rand()**0.51))
                ops = old[:cut]
                deleted = old[cut:]
                for op in deleted:
                    flip(op,board,occ)
                    value -= weight[op[1]]
                if rand()<0.76:
                    tabu[old[cut][1]] = 1.5+2.3*rand()
                if rand()<0.18:
                    recover = deleted
                    retention = 0.64+0.31*rand()
            else:
                if mode<0.65:
                    anchor = old[rr(length)][1]
                    x,y = xs[anchor],ys[anchor]
                    rad = 1+int(9*rand()**1.75*n/45)
                    prob = 0.28+0.72*rand()
                    seeds = {anchor}
                    for op in old:
                        a = op[1]
                        if abs(xs[a]-x)+abs(ys[a]-y)<=rad and rand()<prob:
                            seeds.add(a)
                else:
                    count = min(length,1+int((7 if mode<0.84 else 21)*rand()**1.82))
                    seeds = {old[j][1] for j in rng.sample(range(length),count)}
                removal = 0
                # The cached transitive closure also handles a seed whose
                # descendants are spread across several distant regions.
                _,dependencies,_ = indices(old)
                for a in seeds:
                    removal |= dependencies[a]
                ops,deleted = [],[]
                last = 0
                while removal:
                    bit = removal&-removal
                    removal ^= bit
                    j = bit.bit_length()-1
                    ops.extend(old[last:j])
                    op = old[j]
                    flip(op,board,occ)
                    deleted.append(op)
                    value -= weight[op[1]]
                    last = j+1
                ops.extend(old[last:])
                if rand()<0.87:
                    tabu = dict.fromkeys(seeds,1.25+2.45*rand())
                if rand()<0.50:
                    recover = deleted
                    retention = 0.46+0.44*rand()

        result = grow(ops,board,occ,value,style(i,fresh),tabu,before,recover,retention)
        value = result[0]
        if value>best[0]:
            best = result
            stagnation = 0
        else:
            stagnation += 1
        if ops and (not elite or (value>=0.937*best[0] and all(
                abs(value-e[0])>max(12,value*0.00135) for e in elite))):
            elite.append(result)
            elite.sort(key=lambda e:e[0],reverse=True)
            del elite[7:]

        if ops and (fresh or lane_idx>=0 or (i&15==0 and value>=0.97*best[0])):
            if lane_idx>=0:
                peak,points,walker = lanes[lane_idx]
                delta = walker[0]-value
                if value>peak[0]:
                    lanes[lane_idx] = result,frozenset(op[1] for op in ops),result
                    lanes.sort(key=lambda e:e[0][0],reverse=True)
                elif value>peak[0]*(0.943+0.025*(1-cooling)) and (
                        delta<=0 or rand()<math.exp(-delta/max(1,peak[0]*(0.003+0.011*cooling)))):
                    lanes[lane_idx] = peak,points,result
                elif walker[0]<peak[0] and rand()<0.11:
                    lanes[lane_idx] = peak,points,peak
            else:
                pts = frozenset(op[1] for op in ops)
                for j,(peak,points,walker) in enumerate(lanes):
                    if len(pts^points)<max(5,len(pts)//7):
                        if value>peak[0]:
                            lanes[j] = result,pts,result
                        break
                else:
                    lanes.append((result,pts,result))
                lanes.sort(key=lambda e:e[0][0],reverse=True)
                del lanes[7:]

        delta = current[0]-value
        temp = best[0]*(0.0019+0.0099*cooling)
        if stagnation>86:
            temp *= 1.28
        if delta<=0 or (not fresh and delta<best[0]*0.064 and
                       rand()<math.exp(-delta/max(1,temp))):
            current = result
        if current[0]<best[0]*(0.931+0.049*(1-cooling)):
            current = best
        i += 1

    out = [str(len(best[1]))]
    for op in best[1]:
        a,b,c,d = op[1:5]
        out.append(f"{xs[a]} {ys[a]} {xs[b]} {ys[b]} {xs[c]} {ys[c]} {xs[d]} {ys[d]}")
    sys.stdout.write("\n".join(out)+"\n")


if __name__ == "__main__":
    main()
