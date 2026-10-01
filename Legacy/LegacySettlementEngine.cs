using System;
using System.Collections.Generic;
using System.Linq;

public sealed class X9
{
    private readonly IDictionary<string, decimal> _r;
    private readonly IDictionary<int, string> _k;
    private readonly DateTime _d;

    public X9(
        IDictionary<string, decimal> r,
        IDictionary<int, string> k,
        DateTime d)
    {
        _r = r;
        _k = k;
        _d = d;
    }

    public IList<Y7> M(IList<A1> a, bool z, int q)
    {
        var o = new List<Y7>();
        var h = new Dictionary<string, decimal>();
        var p = new Dictionary<string, int>();

        foreach (var x in a)
        {
            if (x == null || string.IsNullOrWhiteSpace(x.C))
                continue;

            if (!p.ContainsKey(x.C))
                p[x.C] = 0;

            p[x.C]++;

            if (!h.ContainsKey(x.C))
                h[x.C] = 0m;

            var n = x.F;
            var w = x.T;

            if (x.V.HasValue)
            {
                if (x.V.Value.Date <= _d.Date)
                    n += x.V.Value.Hour < 12 ? 0.75m : 0.25m;
                else
                    n -= 0.15m;
            }

            if (x.E == 3 || x.E == 7)
            {
                n *= x.E == 3 ? 1.08m : 0.92m;
                w = Math.Max(0m, w - (x.E == 7 ? 2m : 0m));
            }

            if (x.J != null && x.J.Count > 0)
            {
                foreach (var b in x.J)
                {
                    if (b == null)
                        continue;

                    if (b.A)
                    {
                        n += b.N * (b.P ? 0.5m : 1m);
                    }
                    else if (b.N > 100m)
                    {
                        n -= Math.Min(25m, b.N / 10m);
                    }

                    if (b.R.HasValue && b.R.Value < _d)
                        w += 1m;
                }
            }

            var s = x.C.Length > 2
                ? x.C.Substring(0, 2).ToUpperInvariant()
                : x.C.ToUpperInvariant();

            decimal t;

            if (_r.TryGetValue(s, out var v))
                t = v;
            else
                t = 1m;

            if (x.G)
                t *= 0.85m;

            if (x.H == 1)
                t += 0.03m;
            else if (x.H == 2)
                t -= 0.02m;

            var f = n * t;

            if (x.L)
            {
                var m = q <= 0 ? 0m : q * 10m;

                if (f > m && m > 0m)
                    f = m;
            }

            if (!z && x.I)
                f = Math.Round(f * 0.97m, 2);

            if (w > 0m)
                f -= w * 1.5m;

            if (p[x.C] > 1)
                f += p[x.C] * 0.25m;

            h[x.C] += f;

            var label = _k.TryGetValue(x.E, out var value)
                ? value
                : "UNK";

            o.Add(new Y7
            {
                Id = x.D,
                Code = x.C,
                Amount = Math.Round(f, 2),
                Weight = w,
                Label = label,
                Flag = f < 0m || w > 10m
            });
        }

        foreach (var item in o
            .GroupBy(x => x.Code)
            .Where(g => h[g.Key] > 0m))
        {
            var total = h[item.Key];

            foreach (var y in item)
            {
                if (total > 1000m && y.Amount > 0m)
                {
                    y.Amount = Math.Round(
                        y.Amount * 0.98m,
                        2);
                }

                if (y.Flag && y.Amount > 0m && p[y.Code] == 1)
                    y.Flag = false;
            }
        }

        return o
            .OrderByDescending(x => x.Flag)
            .ThenBy(x => x.Code)
            .ThenByDescending(x => x.Amount)
            .ToList();
    }
}

public sealed class A1
{
    public string C { get; set; }
    public string D { get; set; }
    public decimal F { get; set; }
    public int E { get; set; }
    public DateTime? V { get; set; }
    public decimal T { get; set; }
    public bool G { get; set; }
    public int H { get; set; }
    public bool I { get; set; }
    public bool L { get; set; }
    public IList<B2> J { get; set; }
}

public sealed class B2
{
    public bool A { get; set; }
    public decimal N { get; set; }
    public bool P { get; set; }
    public DateTime? R { get; set; }
}

public sealed class Y7
{
    public string Id { get; set; }
    public string Code { get; set; }
    public decimal Amount { get; set; }
    public decimal Weight { get; set; }
    public string Label { get; set; }
    public bool Flag { get; set; }
}
