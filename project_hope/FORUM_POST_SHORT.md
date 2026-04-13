**Looking for feedback on a structural pattern: herbal roots inside pharma compounds**

I ran a computational parse of the full ZL v3b text and found something I'd like expert eyes on.

Each herbal folio starts with a unique word (f26v = `pched`, f48v = `pcheod`, f9v = `foch`). These same roots reappear embedded inside pharma compound words:

```
Herbal f26v:   pched              (standalone, the plant's code)
Pharma:        o.pched.y          (prefix + root + suffix)
               pched.al           (root + suffix)
```

53% of pharma openers (154/286) contain a herbal root. Compounds decompose as prefix (logogram) + root (content) + suffix (grammar). This is ID-agnostic: the pattern holds regardless of which plant is which.

I'm aware of King-Andrisani, Lunazzi's brachigraphy, and Stolfi's PAAFU. This seems to go beyond paragraph-initial position since it links two sections structurally, but I may be missing something obvious.

Has this herbal-pharma substring link been discussed before? Does it hold up?

Paper: [DOI 10.5281/zenodo.19543917](https://doi.org/10.5281/zenodo.19543917) | Code: [github.com/CorwinFr/Voynich](https://github.com/CorwinFr/Voynich)
