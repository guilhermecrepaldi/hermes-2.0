# INDEX NEWS — Image Sources Reference

## Brand Logos (Wikipedia Commons SVG)
All logos should use the SVG version for crisp rendering at any size.

| Brand | Direct URL |
|-------|-----------|
| NVIDIA | https://upload.wikimedia.org/wikipedia/commons/2/21/Nvidia_logo.svg |
| Apple | https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg |
| Anthropic | https://upload.wikimedia.org/wikipedia/commons/7/78/Anthropic_logo.svg |
| Microsoft | https://upload.wikimedia.org/wikipedia/commons/4/44/Microsoft_logo.svg |
| Meta/Facebook | https://upload.wikimedia.org/wikipedia/commons/7/7b/Meta_Platforms_Inc._logo.svg |
| GitHub | https://upload.wikimedia.org/wikipedia/commons/c/c2/GitHub_Invertocat_Logo.svg |
| Hugging Face | https://upload.wikimedia.org/wikipedia/en/4/45/Hugging_Face_logo.svg |
| Cohere | https://upload.wikimedia.org/wikipedia/en/0/0c/Cohere_logo.svg |
| LangChain | https://upload.wikimedia.org/wikipedia/commons/6/60/LangChain_Logo.svg |
| SK Hynix | https://upload.wikimedia.org/wikipedia/commons/2/24/SK_Hynix.svg |
| NAVER | https://upload.wikimedia.org/wikipedia/commons/2/23/Naver_Logotype.svg |
| LG | https://upload.wikimedia.org/wikipedia/commons/8/8d/LG_logo_%282014%29.svg |
| SK Telecom | https://upload.wikimedia.org/wikipedia/commons/2/2d/SK_Telecom_Logo.svg |

## CEO / Influencer Photos (Wikipedia Commons)
To extract the full-size URL from Wikipedia:
1. Navigate to the person's Wikipedia page
2. Click the infobox image to open the media viewer
3. Remove `/thumb/` from the path and the `/{width}px-{filename}` suffix

| Person | Direct URL |
|--------|-----------|
| Jensen Huang | https://upload.wikimedia.org/wikipedia/commons/e/e6/Jen-Hsun_Huang_2025.jpg |
| Sam Altman | https://upload.wikimedia.org/wikipedia/commons/5/5a/Meeting_with_Masayoshi_Son_and_Sam_Altman_%28February_3%2C_2025%29_%283x4_cropped_on_Altman%29.jpg |
| Dario Amodei | https://upload.wikimedia.org/wikipedia/commons/e/e4/Dario_Amodei_at_TechCrunch_Disrupt_2023_01_%28cropped%29.jpg |
| Satya Nadella | https://upload.wikimedia.org/wikipedia/commons/7/78/MS-Exec-Nadella-Satya-2017-08-31-22_%28cropped%29.jpg |
| Sundar Pichai | https://upload.wikimedia.org/wikipedia/commons/c/c3/Sundar_Pichai_-_2023_%28cropped%29.jpg |
| Tim Cook | https://upload.wikimedia.org/wikipedia/commons/f/f7/Tim_Cook_March_2026_%28cropped_2%29.jpg |
| Andrej Karpathy | https://upload.wikimedia.org/wikipedia/commons/c/c0/Andrej_Karpathy%2C_OpenAI.png |
| Yann LeCun | https://upload.wikimedia.org/wikipedia/commons/8/8e/Laura_Chaubard_%26_Yann_Le_Cun_-_2024_%2853814052697%29_%28cropped%29.jpg |
| Mustafa Suleyman | https://upload.wikimedia.org/wikipedia/commons/2/20/Mustafa_Suleyman_photo_%28cropped%29.jpg |

## Sourcing Pattern for New People/Companies
For a company/person not in the table:
1. Search Wikipedia: `https://en.wikipedia.org/wiki/{Name}`
2. Use browser_console to extract: `document.querySelector('.infobox img')?.src`
3. Replace `/thumb/` with `/` in the path
4. Remove the `/{width}px-{filename}` suffix after the last `/` before the filename
5. Test the URL loads directly

## Event / Chip Photos
- **NVIDIA blog posts** usually have hero images at: `https://blogs.nvidia.com/wp-content/uploads/{year}/{month}/{slug}.jpg`
- **NVIDIA Newsroom press kits**: navigate to the press release, images are in the media gallery
- **Microsoft News**: `https://news.microsoft.com/source/` — images are inline in articles
- **Fallback**: Use CSS gradient background matching the brand colors
