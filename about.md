---
layout: page
title: About Us
cover-img: /assets/img/rarc-hq.png
subtitle: Roseland Amateur Radio Club
---

<style>
/* Responsive layout for the About page. No theme changes or extra assets needed. */
.rarc-feature-image,
.rarc-group-photo {
  margin: 1.25rem auto 1.75rem;
  text-align: center;
}
.rarc-feature-image { max-width: 680px; }
.rarc-group-photo { max-width: 520px; }
.rarc-feature-image img,
.rarc-group-photo img {
  display: block;
  width: 100%;
  height: auto;
  margin: 0 auto;
  border-radius: 5px;
}
.rarc-portrait {
  float: right;
  width: 210px;
  max-width: 38%;
  margin: 0 0 1rem 1.5rem;
  text-align: center;
}
.rarc-portrait img {
  display: block;
  width: 100%;
  height: auto;
  border-radius: 5px;
}
.rarc-portrait figcaption,
.rarc-group-photo figcaption {
  margin-top: .45rem;
  font-size: .88rem;
  line-height: 1.4;
  color: #666;
}
.rarc-side-image {
  float: right;
  width: 240px;
  max-width: 38%;
  height: auto;
  margin: .1rem 0 1rem 1.25rem;
  border-radius: 5px;
}
.rarc-clear { clear: both; }
.rarc-archives { margin: .5rem 0 1.5rem; padding-left: 1.4rem; }
.rarc-archives li { margin-bottom: .45rem; }
.rarc-gallery {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
  max-width: 850px;
  margin: 1.25rem auto;
  align-items: start;
}
.rarc-gallery a { display: block; }
.rarc-gallery img {
  display: block;
  width: 100%;
  height: auto;
  border-radius: 5px;
}

/* Expandable decade history: keyboard-accessible native details elements. */
.rarc-decades { margin: 1rem 0 2rem; }
.rarc-decade {
  margin: .65rem 0;
  border: 1px solid #d3dbe2;
  border-radius: 7px;
  overflow: hidden;
}
.rarc-decade > summary {
  display: list-item;
  padding: .85rem 1.1rem;
  cursor: pointer;
  font-weight: 600;
  line-height: 1.45;
  background: rgba(120, 135, 150, .075);
}
.rarc-decade > summary:hover { background: rgba(120, 135, 150, .13); }
.rarc-decade > summary:focus-visible { outline: 3px solid #357ebd; outline-offset: -3px; }
.rarc-decade[open] > summary { border-bottom: 1px solid #d3dbe2; }
.rarc-decade-body { padding: 1rem 1.15rem .75rem; }
.rarc-decade-body p { margin: 0 0 .9rem; }
.rarc-decade-sources { font-size: .92rem; line-height: 1.55; margin: 0 0 .8rem; }
.rarc-decade-sources li { margin-bottom: .4rem; }
@media (max-width: 640px) {
  .rarc-decade > summary { padding: .85rem .85rem; }
  .rarc-decade-body { padding: .9rem .85rem .5rem; }
}

@media (max-width: 640px) {
  .rarc-portrait,
  .rarc-side-image {
    float: none;
    display: block;
    width: 100%;
    max-width: 320px;
    margin: 1rem auto 1.25rem;
  }
  .rarc-gallery { grid-template-columns: 1fr; gap: .85rem; }
  .rarc-archives { padding-left: 1.2rem; }
}

/* A compact, image-led introduction to today's club. */
.rarc-today-intro { margin: .3rem 0 1.15rem; font-size: 1.05rem; line-height: 1.6; }
.rarc-today-net {
  margin: 1.1rem 0 1.5rem;
  padding: 1rem 1.2rem;
  border-left: 4px solid #47768e;
  border-radius: 0 8px 8px 0;
  background: #f4f7f9;
}
.rarc-today-net h3 { margin: 0 0 .45rem; font-size: 1.23rem; line-height: 1.35; }
.rarc-today-net p { margin: 0 0 .6rem; line-height: 1.56; }
.rarc-today-net p:last-child { margin-bottom: 0; }

/* Keep each photograph and its caption together at every viewport width. */
.rarc-today-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
  align-items: stretch;
  margin: 1.25rem 0 1.5rem;
}
.rarc-today-card {
  display: flex;
  flex-direction: column;
  min-width: 0;
  width: 100%;
  margin: 0;
  border: 1px solid #d7e0e6;
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
}
.rarc-today-card > a {
  display: block;
  flex: 0 0 auto;
  background: #eef2f4;
}
.rarc-today-card img {
  display: block;
  width: 100%;
  height: 172px;
  max-height: 172px;
  object-fit: contain;
  margin: 0;
}
.rarc-today-card-body {
  display: block;
  flex: 1 1 auto;
  min-width: 0;
  padding: .85rem .95rem 1rem;
  background: #fff;
  color: #24313b;
}
.rarc-today-card-body h3 {
  display: block;
  color: #24313b;
  margin: 0 0 .55rem;
  font-size: 1.12rem;
  line-height: 1.3;
}
.rarc-today-card-body p {
  display: block;
  color: #24313b;
  margin: 0 0 .65rem;
  font-size: .96rem;
  line-height: 1.55;
}
.rarc-today-card-body p:last-child { margin-bottom: 0; }
.rarc-today-links { font-size: .9rem !important; line-height: 1.7 !important; }
.rarc-today-outro { margin: 1.2rem 0; line-height: 1.55; }

/* Two cards on intermediate screens; one complete card per row on phones. */
@media (max-width: 900px) {
  .rarc-today-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 640px) {
  .rarc-today-net { padding: .95rem 1rem; }
  .rarc-today-grid { grid-template-columns: minmax(0, 1fr); }
  .rarc-today-card img { height: 180px; max-height: 180px; }
  .rarc-today-card-body { padding: 1rem; }
}

</style>

## Welcome to the Roseland Amateur Radio Club

<figure class="rarc-feature-image">
  <img src="/assets/img/log-1978.jpg" alt="Historical Roseland Amateur Radio Club logbook" loading="lazy">
</figure>

Amateur radio opens the door to a world of discovery. From making contacts across town or around the globe to exploring new technology and experimenting with radios and antennas, there's always something exciting to experience. But some of the best moments come from sharing that excitement with others.

At the Roseland Amateur Radio Club, we bring together people who enjoy radio, technology, learning, and good company. Whether you're making your first contact, exploring a new operating mode, or simply enjoying a friendly conversation on the air, there's always something new to discover and someone happy to share the experience.

Our members represent all amateur radio license classes, and we warmly welcome those who are just discovering the hobby. As an <a href="https://www.arrl.org/" target="_blank" rel="noopener noreferrer">ARRL-affiliated club</a>, we help aspiring operators prepare for their license exams and encourage everyone to learn, experiment, and get involved.

You don't need years of experience to feel at home here. Just bring your curiosity and an interest in joining the fun. Come <a href="/calendar/" target="_blank" rel="noopener noreferrer">visit us at an upcoming meeting</a> and see what amateur radio is all about.

## Our History

<figure class="rarc-portrait">
  <img src="/assets/img/doc-k2gq.jpg" alt="Dr. Milton I. 'Doc' Schwalbe, founder of the club" loading="lazy">
  <figcaption>Dr. Milton I. “Doc” Schwalbe, former holder of K2GQ</figcaption>
</figure>

Our history began in Irvington, New Jersey, in 1946. Over time, we used the Irvington-Roseland Amateur Radio Club name before adopting our present name. The records below offer a look at the people and activities that have shaped our club.

<div class="rarc-clear"></div>

### History by Decade

Select a decade to read about documented club activities and follow links to historical records.

<div class="rarc-decades">

<details class="rarc-decade">
  <summary>1940s — Beginnings in Irvington</summary>
  <div class="rarc-decade-body">
    <p>In 1946, Dr. Milton I. “Doc” Schwalbe founded our club in Irvington as the Irvington Radio Amateur Club (IRAC).</p>
    <p>Doc previously held K2GQ, the call sign we use today. The April 1961 issue of <em>QST</em> identifies him as Dr. Milton I. Schwalbe, W4VP, formerly K2GQ.</p>

    <ul class="rarc-decade-sources">
      <li><a href="https://www.worldradiohistory.com/Archive-DX/QST/60s/QST-1961-04.pdf" target="_blank" rel="noopener noreferrer"><em>QST</em>, April 1961, p. 69</a> — Schwalbe's Silent Key listing.</li>
    </ul>
  </div>
</details>

<details class="rarc-decade">
  <summary>1950s — Classes, Radio Nets, and Field Day</summary>
  <div class="rarc-decade-body">
    <p>By January 1955, we were meeting on the first and third Mondays and offering weekly Morse code and radio theory classes. We used automatic tape machines for code practice and operated a Saturday net on 28.7 MHz.</p>
    <p>We also took part in ARRL Field Day. A photograph in the December 1958 issue of <em>QST</em> shows our members examining a failed generator during that year's event. The caption identifies W2WDZ and our chief operator, W2ZMH. We became an ARRL-affiliated club in 1958.</p>

    <ul class="rarc-decade-sources">
      <li><a href="https://www.worldradiohistory.com/INTERNATIONAL/QST/QST-1955-01.pdf" target="_blank" rel="noopener noreferrer"><em>QST</em>, January 1955, p. 86</a> — meetings, classes, and net.</li>
      <li><a href="https://www.worldradiohistory.com/Archive-DX/QST/50s/QST-1958-12.pdf" target="_blank" rel="noopener noreferrer"><em>QST</em>, December 1958, p. 47</a> — Field Day photograph.</li>
    </ul>
  </div>
</details>

<details class="rarc-decade">
  <summary>1960s — Auctions, Field Day, and Annual Dinners</summary>
  <div class="rarc-decade-body">
    <p>In 1962, we announced plans for an auction to benefit the ARRL's headquarters building fund, with our member K2RXH named as auctioneer in <em>QST</em>.</p>
    <p>We continued holding annual dinners in Irvington, with notices appearing in 1964 and 1968. David Rettig, K2VOB, was a contact for these events.</p>
    <p>We also took part in Field Day. The September 1967 issue of <em>QST</em> lists K2GQ among Northern New Jersey stations that sent Field Day messages to the Section Manager.</p>

    <ul class="rarc-decade-sources">
      <li><a href="https://www.worldradiohistory.com/INTERNATIONAL/QST/QST-1962-07.pdf" target="_blank" rel="noopener noreferrer"><em>QST</em>, July 1962, p. 70</a> — club auction announcement.</li>
      <li><a href="https://www.worldradiohistory.com/Archive-DX/QST/60s/QST-1964-10.pdf" target="_blank" rel="noopener noreferrer"><em>QST</em>, October 1964, p. 15</a> — annual dinner notice.</li>
      <li><a href="https://www.worldradiohistory.com/Archive-DX/QST/60s/QST-1967-09.pdf" target="_blank" rel="noopener noreferrer"><em>QST</em>, September 1967, p. 100</a> — Northern New Jersey Field Day messages.</li>
      <li><a href="https://www.worldradiohistory.com/INTERNATIONAL/QST/QST-1968-10.pdf" target="_blank" rel="noopener noreferrer"><em>QST</em>, October 1968 (annual dinner notice)</a> — later annual dinner announcement.</li>
    </ul>
  </div>
</details>

<details class="rarc-decade">
  <summary>1970s — Mentoring, Field Day, and Hamfests</summary>
  <div class="rarc-decade-body">
    <p>Our first hamfest dates to 1973, when we operated as the Irvington Radio Amateur Club (IRAC). A 1983 notice described that year's gathering as our 11th annual hamfest, supporting 1973 as the starting year. We hosted later hamfests at the Irvington Police Athletic League building, 285 Union Avenue; a 1974 notice listed equipment sales tables, refreshments, and door prizes.</p>
    <p>We continued helping newcomers obtain their licenses. In a later firsthand account, Mark Wiatroski, W2MSW, recalled learning Morse code with our members and taking his Novice examination with Ed Surmaitis, WA2MYZ. Mark received his first call sign, WN2DUX, in early 1976.</p>
    <p>Field Day remained part of our activities. The September 1977 issue of <em>QST</em> reported receiving Field Day messages from IRAC.</p>

    <ul class="rarc-decade-sources">
      <li><a href="https://www.worldradiohistory.com/Archive-DX/73-magazine/73-magazine-1974/73-magazine-04-april-1974.pdf" target="_blank" rel="noopener noreferrer"><em>73 Magazine</em>, April 1974, p. 14</a> — Irvington hamfest announcement.</li>
      <li><a href="https://www.worldradiohistory.com/Archive-All-Amateur/World-Radio/80s/World-Radio-1983-03.pdf" target="_blank" rel="noopener noreferrer"><em>Worldradio</em>, March 1983, p. 48</a> — describes IRAC's 1983 event as its 11th annual hamfest, supporting a 1973 starting year.</li>
      <li><a href="https://www.worldradiohistory.com/Archive-DX/QST/60s/QST-1977-09.pdf" target="_blank" rel="noopener noreferrer"><em>QST</em>, September 1977 (Northern New Jersey section report)</a> — Field Day messages from IRAC.</li>
      <li><a href="https://cwops.org/wp-content/uploads/2021/02/solid-copy-2021.02.3.pdf#page=46" target="_blank" rel="noopener noreferrer"><em>Solid Copy</em>, February 2021, p. 46</a> — Wiatroski's recollection of 1976.</li>
    </ul>
  </div>
</details>

<details class="rarc-decade">
  <summary>1980s — Radio Contesting and Hamfests</summary>
  <div class="rarc-decade-body">
    <p>Our annual hamfests continued during the 1980s. In March 1983, we hosted our 11th annual hamfest at the Irvington Police Athletic League building, 285 Union Avenue. Ed Surmaitis, WA2MYZ, and Joe Barnes, WB2SRY, were the event contacts.</p>
    <p>Our K2GQ operators also entered the ARRL November Sweepstakes, including multioperator CW and phone contests. In 1985, we logged 161 contacts on CW and 414 on phone; the published operator lists included Walt Heineman, W2QR, and Ed Surmaitis, WA2MYZ. In the 1988 Phone Sweepstakes, our team completed 803 contacts across 75 ARRL sections, scoring 120,450 points.</p>
    <p>In March 1988, we hosted a hamfest at American Legion Post 201, 305 Eisenhower Parkway, Livingston, New Jersey.</p>

    <ul class="rarc-decade-sources">
      <li><a href="https://www.worldradiohistory.com/Archive-All-Amateur/World-Radio/80s/World-Radio-1983-03.pdf" target="_blank" rel="noopener noreferrer"><em>Worldradio</em>, March 1983, p. 48</a> — 11th annual Irvington hamfest.</li>
      <li><a href="https://contests.arrl.org/ContestResults/1985/SS-CW-1985-FinalQSTResults.pdf#page=3" target="_blank" rel="noopener noreferrer"><em>QST</em>, May 1986, pp. 82 and 84</a> — 1985 CW and phone Sweepstakes results and operator listings.</li>
      <li><a href="https://www.worldradiohistory.com/Archive-DX/QST/80s/QST-1988-03.pdf" target="_blank" rel="noopener noreferrer"><em>QST</em>, March 1988 (hamfest calendar)</a> — Livingston hamfest announcement.</li>
      <li><a href="https://contests.arrl.org/ContestResults/1988/SS-Phone-1988-FinalQSTResults.pdf#page=7" target="_blank" rel="noopener noreferrer"><em>QST</em>, May 1989, p. 99</a> — 1988 Phone Sweepstakes score and operators.</li>
    </ul>
  </div>
</details>

<details class="rarc-decade">
  <summary>1990s — Club Events and WEARC's Founding</summary>
  <div class="rarc-decade-body">
    <p>On March 23, 1991, we hosted a hamfest at West Orange High School, 600 Pleasant Valley Way. A February newsletter named Walt Heineman as our contact and gave a mailing address in Essex Fells.</p>
    <p>Our club appeared in the ARRL Affiliated Club Competition results for the 1992 November Sweepstakes.</p>
    <p>In 1994, several of our members helped establish a separate organization, the West Essex Amateur Radio Club (WEARC). WEARC founding member Mike Hartmann, NI2S, later described its formation in a remembrance of John Weinfeldt, N2NO. Weinfeldt had participated in IRAC before joining WEARC, where he later served as president.</p>
    <p>We continued hosting hamfests at West Orange High School. A March 1997 notice listed Jim Howe, N2TDI, and Liz Howe, N2WGH, as contacts.</p>

    <ul class="rarc-decade-sources">
      <li><a href="https://nparc.org/newsletters/Jan91MSG.pdf#page=3" target="_blank" rel="noopener noreferrer"><em>Mountain Spark Gaps</em>, February 1991, p. 3</a> — West Orange hamfest announcement.</li>
      <li><a href="https://contests.arrl.org/ContestResults/1992/SS-Phone-1992-FinalQSTResults.pdf" target="_blank" rel="noopener noreferrer"><em>QST</em>, May 1993, p. 112</a> — 1992 Sweepstakes club competition.</li>
      <li><a href="https://www.arimi.it/wp-content/73/03_March_1997.pdf" target="_blank" rel="noopener noreferrer"><em>73 Magazine</em>, March 1997 (special events listing)</a> — West Orange hamfest notice.</li>
      <li><a href="https://wearc.org/about-us/" target="_blank" rel="noopener noreferrer">WEARC — About Us</a> — dates the club's founding to 1994.</li>
      <li><a href="https://wearc.org/silent-keys/john-weinfeld-n2no/" target="_blank" rel="noopener noreferrer">WEARC — Remembering John Weinfeldt, N2NO</a> — Mike Hartmann's firsthand account of WEARC's formation.</li>
    </ul>
  </div>
</details>

<details class="rarc-decade">
  <summary>2000s — Special Events and Historic Sites</summary>
  <div class="rarc-decade-body">
    <p>During the 2000s, we participated in special events and radio demonstrations at Sandy Hook, New Jersey. For Fort Hancock Days in October 2008, the National Park Service announced plans for our members to demonstrate shortwave communications on the grounds of Sandy Hook Lighthouse.</p>
    <p>We also advertised our K2A special-event station for Fort Hancock Establishment Day on October 26, 2008, with plans to operate on the 20- and 40-meter bands.</p>

    <ul class="rarc-decade-sources">
      <li><a href="https://www.nps.gov/gate/learn/news/2008-fort-hancock-days-at-sandy-hook.htm" target="_blank" rel="noopener noreferrer">National Park Service, October 2008</a> — Fort Hancock Days amateur radio demonstration.</li>
      <li><a href="https://www.arrl.org/special_events/search/page%3A113/Date.start%3A1969-12-31/Date.end%3A2015-03-31/model%3AEvent" target="_blank" rel="noopener noreferrer">ARRL, October 26, 2008</a> — K2A special-event listing.</li>
    </ul>
  </div>
</details>

<details class="rarc-decade">
  <summary>2010s — Special Events and the 70th Anniversary</summary>
  <div class="rarc-decade-body">
    <p>In September 2014, we advertised a K2R special-event operation at Eagle Rock Reservation in West Orange.</p>
    <p>In 2015, we renewed our focus on emergency communications and service to our community, as highlighted in a 2016 local news feature. For our 70th anniversary in May 2016, we also planned a QSO party using K2GQ, with activity advertised on the 20- and 40-meter bands.</p>

    <ul class="rarc-decade-sources">
      <li><a href="https://www.arrl.org/special_events/search/page%3A17/Date.start%3A2014-07-01/Date.end%3A2023-03-21/model%3AEvent" target="_blank" rel="noopener noreferrer">ARRL, September 2014</a> — K2R special-event listing.</li>
      <li><a href="https://www.arrl.org/special_events/search/page%3A100/Date.start%3A2014-07-01/Date.end%3A2023-12-03/model%3AEvent" target="_blank" rel="noopener noreferrer">ARRL, May 2016</a> — 70th-anniversary announcement.</li>
      <li><a href="https://essexnewsdaily.com/news/roseland/explore-the-world-through-a-ham-radio/" target="_blank" rel="noopener noreferrer"><em>Essex News Daily</em>, May 2016</a> — club activities and anniversary reporting.</li>
    </ul>
  </div>
</details>

<details class="rarc-decade">
  <summary>2020s — Public Service and Portable Operating</summary>
  <div class="rarc-decade-body">
    <p>In 2023, we established our Community Amateur Radio Social Net, bringing local and regional operators together for a friendly weekly conversation.</p>
    <p>In October 2024, our members operated portable from South Mountain Reservation with a 10-meter transceiver, using SSB and FT8.</p>
    <p>In May 2025, we provided communications support for the Caldwell Classic 5K. In June 2026, our members joined an Essex County ARES rapid-deployment exercise at Eagle Rock Reservation, using portable stations, repeater and simplex contacts, and message handling.</p>

    <ul class="rarc-decade-sources">
      <li><a href="/2023-11-08-tuesday-night-net/" target="_blank" rel="noopener noreferrer">November 2023 Community Net report</a> — early check-ins on our weekly social net.</li>
      <li><a href="/2024-10-26-portable-operation/" target="_blank" rel="noopener noreferrer">October 2024 portable operation</a> — club report and photographs.</li>
      <li><a href="/2025-05-17-caldwell-classic/" target="_blank" rel="noopener noreferrer">May 2025 Caldwell Classic 5K</a> — public service report.</li>
      <li><a href="/2026-06-06-ares-eagle-rock/" target="_blank" rel="noopener noreferrer">June 2026 ARES exercise</a> — field exercise report.</li>
    </ul>
  </div>
</details>

</div>

## The Club Today

<p class="rarc-today-intro">For us, amateur radio is about people as much as technology. We get on the air, share what we learn, and put our skills to work for neighbors throughout Essex County. There is always something to discover—and plenty of room for new faces.</p>

<section class="rarc-today-net" aria-labelledby="rarc-today-net-title">
  <h3 id="rarc-today-net-title">Join the conversation every Tuesday</h3>
  <p>Since 2023, our Community Amateur Radio Social Net has connected local and regional operators for friendly conversation. Join us <strong>Tuesdays at 7:30 PM Eastern</strong> on <strong>KC2TXA/R (146.595 MHz)</strong> or through <strong>EchoLink KC2TXA-R</strong>. All licensed operators are welcome.</p>
  <p><a href="#net">Net frequencies and details</a> · <a href="/netreports/" target="_blank" rel="noopener noreferrer">Weekly net reports</a></p>
</section>

<div class="rarc-today-grid">
  <figure class="rarc-today-card">
    <a href="/2024-01-29-new-radio/" target="_blank" rel="noopener noreferrer" aria-label="Read about our Yaesu FTDX10 station upgrade">
      <img src="/assets/img/ftdx10_club.jpg" alt="Amateur radio equipment at the Roseland ARC club station" loading="lazy">
    </a>
    <figcaption class="rarc-today-card-body">
      <h3>Learn and experiment</h3>
      <p>Our members share experience through station projects, practical demonstrations, and talks on everything from propagation and Morse code to digital operating.</p>
      <p class="rarc-today-links"><a href="/2024-03-21-gene-kji-presentation/" target="_blank" rel="noopener noreferrer">Propagation</a> · <a href="/2024-05-15-bob-auf-presentation/" target="_blank" rel="noopener noreferrer">CW</a> · <a href="/2024-07-17-jesse-ugk-presentation/" target="_blank" rel="noopener noreferrer">FT8</a> · <a href="/2024-01-29-new-radio/" target="_blank" rel="noopener noreferrer">Station upgrade</a></p>
    </figcaption>
  </figure>

  <figure class="rarc-today-card">
    <a href="/2026-04-18-s-mtn-meet-up/" target="_blank" rel="noopener noreferrer" aria-label="Read about our South Mountain portable operating meetup">
      <img src="/assets/img/2026-april-smtn/IMG_0742.jpeg" alt="A South Mountain Reservation amateur radio meetup" loading="lazy">
    </a>
    <figcaption class="rarc-today-card-body">
      <h3>Get outdoors and on the air</h3>
      <p>Portable operations bring our members together to test antennas, batteries, and HF equipment—often alongside friends from WEARC, NPARC, and neighboring clubs.</p>
      <p class="rarc-today-links"><a href="/2024-10-26-portable-operation/" target="_blank" rel="noopener noreferrer">2024 activation</a> · <a href="/2026-04-18-s-mtn-meet-up/" target="_blank" rel="noopener noreferrer">April meetup</a> · <a href="/2026-05-16-s-mtn-meet-up-may/" target="_blank" rel="noopener noreferrer">May meetup</a></p>
    </figcaption>
  </figure>

  <figure class="rarc-today-card">
    <a href="/2026-10-17-roseland-run/" target="_blank" rel="noopener noreferrer" aria-label="Read about our communications support for the Lou LaSalle Memorial 5K">
      <img src="/assets/img/2026-roseland-run/rr-1c.jpeg" alt="Roseland's 2026 community 5K event" loading="lazy">
    </a>
    <figcaption class="rarc-today-card-body">
      <h3>Serve our neighbors</h3>
      <p>We support local races with reliable communications and build readiness through practical emergency communications exercises.</p>
      <p class="rarc-today-links"><a href="/2025-05-17-caldwell-classic/" target="_blank" rel="noopener noreferrer">Caldwell Classic</a> · <a href="/2026-10-17-roseland-run/" target="_blank" rel="noopener noreferrer">Roseland 5K</a> · <a href="/2026-06-06-ares-eagle-rock/" target="_blank" rel="noopener noreferrer">ARES exercise</a></p>
    </figcaption>
  </figure>
</div>

<p class="rarc-today-outro">The best part of our club is the people. Whether you're newly licensed, returning to radio, or have years of experience, we'd enjoy meeting you. <a href="/calendar/" target="_blank" rel="noopener noreferrer">Visit us at an upcoming meeting.</a></p>

<figure class="rarc-group-photo">
  <a href="/assets/img/rarc-dec-2025-holiday-party.jpeg" target="_blank" rel="noopener noreferrer">
    <img src="/assets/img/rarc-dec-2025-holiday-party.jpeg" alt="Roseland Amateur Radio Club holiday gathering, December 2025" loading="lazy">
  </a>
  <figcaption>Club holiday gathering, December 2025</figcaption>
</figure>

---

## Club Officers

| Position | Name | Call Sign |
| :------ | :--- | :-------- |
| President | Bob Calandra | K2AUF |
| Vice President | Ronald Reinhardt | WV2RJR |
| Secretary | Maurice Naraine | KB2SUL |
| Treasurer | Jesse Bertier | N1UGK |
| License Custodian | Peter Summers | N2XTT |

**Email:** <a href="mailto:roselandarc@gmail.com">roselandarc@gmail.com</a>

---

## Meetings and Membership

<img class="rarc-side-image" src="/assets/img/radio-station.png" alt="Amateur radio station illustration" loading="lazy">

**In-person meetings:**  
Roseland Office of Emergency Management  
<a href="https://maps.app.goo.gl/nUBc3FntGjyRNM9u7" target="_blank" rel="noopener noreferrer">300 Eagle Rock Avenue, Roseland, NJ 07068-1719</a>

**Join us online:** <a href="https://us06web.zoom.us/j/82056566411?pwd=vAeRMSWjVCsRWea1EpPdWWkEBHmKKo.1" target="_blank" rel="noopener noreferrer">Zoom meeting link</a>

Guests and new members are always welcome. Please check the <a href="/calendar/" target="_blank" rel="noopener noreferrer">club calendar</a> to confirm the next meeting date.

<a href="https://groups.google.com/g/K2GQ" target="_blank" rel="noopener noreferrer">Join our Google Group</a> to participate in the club's email discussion list.

<div class="rarc-clear"></div>

---

<h2 id="net">Weekly Community Net</h2>

<a href="/netreports/" aria-label="View weekly net reports" target="_blank" rel="noopener noreferrer"><img class="rarc-side-image" src="/assets/img/scanner.jpg" alt="Radio scanner" loading="lazy"></a>

**Tuesdays at 7:30 PM Eastern Time — open to all.**

Livingston: <a href="https://www.repeaterbook.com/repeaters/details.php?state_id=34&ID=2845" target="_blank" rel="noopener noreferrer">146.595 MHz (+1.0 MHz), 100.0 Hz</a>  
Newark: <a href="https://www.repeaterbook.com/repeaters/details.php?state_id=34&ID=2847" target="_blank" rel="noopener noreferrer">147.225 MHz (+0.6 MHz), 141.3 Hz</a>  
EchoLink: **KC2TXA-R**

We thank and honor <a href="https://www.menorahchapelsatmillburn.com/obituaries/Alvin-Friedland-MD?obId=29432650" target="_blank" rel="noopener noreferrer">Dr. Alvin Friedland, NE2S</a>; <a href="https://www.legacy.com/us/obituaries/starledger/name/george-murillo-obituary?id=8886223" target="_blank" rel="noopener noreferrer">George Murillo Jr., W2PQC</a>; the <a href="/sbarc/" target="_blank" rel="noopener noreferrer">St. Barnabas Amateur Radio Club</a>; and the <a href="/assets/img/nparc-ne2s-2007.png" target="_blank" rel="noopener noreferrer">St. Barnabas control operators</a> for their contributions to amateur radio and the use of their repeater for the weekly community net.

<div class="rarc-clear"></div>

<figure class="rarc-group-photo">
  <a href="/assets/img/SBARC-August-1984.png" target="_blank" rel="noopener noreferrer">
    <img src="/assets/img/SBARC-August-1984.png" alt="St. Barnabas Amateur Radio Club members in August 1984" loading="lazy">
  </a>
  <figcaption>St. Barnabas Amateur Radio Club — August 1984</figcaption>
</figure>

We also thank <a href="https://k2mff.njit.edu/" target="_blank" rel="noopener noreferrer">NJIT's Amateur Radio Club</a>, K2MFF, for the use of its repeater for the weekly community net. Based at NJIT in Newark, the club operates a VHF repeater (147.225 MHz, +0.600 MHz offset, 141.3 Hz tone; EchoLink K2MFF-R), maintains an amateur radio station, supports licensing and public-service activities, and participates in HamSCI radio-science projects.

---

<h2 id="legacy">Roseland Legacy Event Photos</h2>

Select a photograph to view the full-size image.

<div class="rarc-gallery">
  <a href="/assets/img/legacy/IMG_0673.JPG" target="_blank" rel="noopener noreferrer"><img src="/assets/img/legacy/IMG_0673.JPG" alt="Historic Roseland Amateur Radio Club event photo 1" loading="lazy"></a>
  <a href="/assets/img/legacy/img_0818X.jpg" target="_blank" rel="noopener noreferrer"><img src="/assets/img/legacy/img_0818X.jpg" alt="Historic Roseland Amateur Radio Club event photo 2" loading="lazy"></a>
  <a href="/assets/img/legacy/iracparade.jpg" target="_blank" rel="noopener noreferrer"><img src="/assets/img/legacy/iracparade.jpg" alt="Irvington Radio Amateur Club parade" loading="lazy"></a>
  <a href="/assets/img/legacy/nno.jpg" target="_blank" rel="noopener noreferrer"><img src="/assets/img/legacy/nno.jpg" alt="Historic club community event" loading="lazy"></a>
</div>
