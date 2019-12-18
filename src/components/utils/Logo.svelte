<script>
    export let jq;
    jq(document).ready(()=>{
        function fitElementToParent(el, padding, exception) {
            let timeout = null;
            function resize() {
                if (timeout) clearTimeout(timeout);
                anime.set(el, {scale: 1});
                if (exception) anime.set(exception, {scale: 1});
                let pad = padding || 0;
                let parentEl = el.parentNode;
                let elOffsetWidth = el.offsetWidth - pad;
                let parentOffsetWidth = parentEl.offsetWidth;
                let ratio = parentOffsetWidth / elOffsetWidth;
                let invertedRatio = elOffsetWidth / parentOffsetWidth;
                timeout = setTimeout(function() {
                anime.set(el, {scale: ratio});
                if (exception) anime.set(exception, {scale: invertedRatio});
                }, 10);
            }
            resize();
            window.addEventListener('resize', resize);
        }
        // main logo animation
        let logoAnimation = (function() {
        
            let logoAnimationEl = document.querySelector('.logo-animation');
            let bouncePath = anime.path('.bounce path');
            
            fitElementToParent(logoAnimationEl, 0, '.bounce svg');
            
            anime.set(['.letter-a', '.letter-n', '.letter-i'], {translateX: 70});
            anime.set('.letter-e', {translateX: -70});
            anime.set('.dot', { translateX: 630, translateY: -200 });
            
            let logoAnimationTL = anime.timeline({
                autoplay: false,
                easing: 'easeOutSine'
            })
            .add({
                targets: '.letter-i .line',
                duration: 0,
                begin: function(a) { a.animatables[0].target.removeAttribute('stroke-dasharray'); }
            }, 0)
            .add({
                targets: '.bounced',
                transformOrigin: ['50% 100% 0px', '50% 100% 0px'],
                translateY: [
                {value: [150, -160], duration: 190, endDelay: 20, easing: 'cubicBezier(0.225, 1, 0.915, 0.980)'},
                {value: 4, duration: 120, easing: 'easeInQuad'},
                {value: 0, duration: 120, easing: 'easeOutQuad'}
                ],
                scaleX: [
                {value: [.25, .85], duration: 190, easing: 'easeOutQuad'},
                {value: 1.08, duration: 120, delay: 85, easing: 'easeInOutSine'},
                {value: 1, duration: 260, delay: 25, easing: 'easeOutQuad'}
                ],
                scaleY: [
                {value: [.3, .8], duration: 120, easing: 'easeOutSine'},
                {value: .35, duration: 120, delay: 180, easing: 'easeInOutSine'},
                {value: .57, duration: 180, delay: 25, easing: 'easeOutQuad'},
                {value: .5, duration: 190, delay: 15, easing: 'easeOutQuad'}
                ],
                delay: anime.stagger(80)
            }, 1000)
            .add({
                targets: '.dot',
                opacity: { value: 1, duration: 100 },
                translateY: 250,
                scaleY: [4, .7],
                scaleX: { value: 1.3, delay: 100, duration: 200},
                duration: 280,
                easing: 'cubicBezier(0.350, 0.560, 0.305, 1)'
            }, '-=290')
            .add({
                targets: '.letter-m .line',
                easing: 'easeOutElastic(1, .8)',
                duration: 600,
                d: function(el) { return el.dataset.d2 },
                begin: function(a) { a.animatables[0].target.removeAttribute('stroke-dasharray'); }
            }, '-=140')
            .add({
                targets: ['.letter-a', '.letter-n', '.letter-i', '.letter-e'],
                translateX: 0,
                easing: 'easeOutElastic(1, .6)',
                duration: 800,
                delay: anime.stagger(40, {from: 2.5}),
                change: function(a) { a.animatables[2].target.removeAttribute('stroke-dasharray'); }
            }, '-=600')
            .add({
                targets: '.letter-m .line',
                d: function(el) { return el.dataset.d3 },
                easing: 'spring(.2, 200, 3, 60)',
            }, '-=680')
            .add({
                targets: '.dot',
                translateX: bouncePath('x'),
                translateY: bouncePath('y'),
                rotate: {value: '1turn', duration: 790},
                scaleX: { value: 1, duration: 50, easing: 'easeOutSine' },
                scaleY: [
                { value: [1, 1.5], duration: 50, easing: 'easeInSine' },
                { value: 1, duration: 50, easing: 'easeOutExpo' }
                ],
                easing: 'cubicBezier(0, .74, 1, .255)',
                duration: 800
            }, '-=1273')
            .add({
                targets: '.dot',
                scale: 1,
                rotate: '1turn',
                scaleY: {value: .5, delay: 0, duration: 150, delay: 230},
                translateX: 430,
                translateY: [
                {value: 244, duration: 100},
                {value: 204, duration: 200, delay: 130},
                {value: 224, duration: 225, easing: 'easeOutQuad', delay: 25}
                ],
                duration: 200,
                easing: 'easeOutSine'
            }, '-=474')
            .add({
                targets: '.letter-i .line',
                transformOrigin: ['50% 100% 0', '50% 100% 0'],
                d: function(el) { return el.dataset.d2 },
                easing: 'cubicBezier(0.400, 0.530, 0.070, 1)',
                duration: 80
            }, '-=670')
            .add({
                targets: '.logo-letter',
                translateY: [
                {value: 40, duration: 150, easing: 'easeOutQuart'},
                {value: 0, duration: 800, easing: 'easeOutElastic(1, .5)'}
                ],
                strokeDashoffset: [anime.setDashoffset, 0],
                delay: anime.stagger(60, {from: 'center'})
            }, '-=670')
            .add({
                targets: '.bounced',
                scaleY: [
                {value: .4, duration: 150, easing: 'easeOutQuart'},
                {value: .5, duration: 800, easing: 'easeOutElastic(1, .5)'}
                ],
                delay: anime.stagger(60, {from: 'center'})
            }, '-=1090')
            .add({
                targets: '.logo-text',
                translateY: [
                {value: 20, easing: 'easeOutQuad', duration: 100},
                {value: 0, easing: 'easeOutElastic(1, .9)', duration: 450}
                ],
                opacity: {value: [0.001, 1], duration: 50},
                duration: 500
            }, '-=970')
            .add({
                targets: '.main-logo-circle',
                opacity: {value: [0.001, 1], duration: 1500},
                backgroundImage: ['linear-gradient(-135deg, #FFFFFF 50%, #F6F4F2 75%, #F6F4F2 100%, #DDDAD7 100%)', 'linear-gradient(-135deg, #FFFFFF 5%, #F6F4F2 40%, #F6F4F2 70%, #DDDAD7 100%)'],
                translateY: {value: ['60px', 0], easing: 'cubicBezier(0.175, 0.865, 0.245, 0.840)'},
                duration: 2000,
                easing: 'easeInOutQuad'
            }, '-=970')
            .add({
                targets: ['.description-title','.description-paragraph'],
                opacity: {value: [0.001, 1], easing: 'cubicBezier(0.175, 0.865, 0.245, 0.840)'},
                translateY: {value: ['80px', 0], easing: 'cubicBezier(0.175, 0.865, 0.245, 0.840)'},
                duration: 3500,
                delay: anime.stagger(75)
            }, '-=1300')
            
            return logoAnimationTL;
        
        })();
        logoAnimation.play();

    })

</script>

<style>
  .main-logo {
    position: relative;
    display: flex;
    flex-direction: column;
    width: 100%;
    max-width: 600px;
    margin: auto;
  }

  .logo-animation-wrapper {
    position: relative;
    width: 100%;
    padding-bottom: 12%;
    
  }

  .logo-animation {
    pointer-events: none;
    overflow: visible;
    display: flex;
    flex-shrink: 0;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    position: absolute;
    top: 50%;
    left: 50%;
    width: 1000px;
    height: 240px;
    margin: -120px 0 0 -500px;
    transform: scale(.633333);
  }

  .anime-logo {
    overflow: visible;
    position: relative;
    display: flex;
    flex-direction: column;
    width: 1000px;
    height: 120px;
  }

  .anime-logo-signs {
    overflow: visible;
    display: flex;
    align-items: flex-end;
    position: relative;
    width: 100%;
    height: 512px;
    margin-top: -352px;
  }

  .logo-letter {
    display: flex;
    align-items: flex-end;
    overflow: hidden;
    height: 100%;
  }

  .bounced {
    transform-origin: 50% 100% 0px;
    transform: translateY(200px) scaleX(.55) scaleY(.8);
  }

  .logo-animation .bounce {
    overflow: visible;
    position: absolute;
    left: 0;
    bottom: 70px;
    /*stroke: red;*/
  }

  .logo-animation .dot {
    opacity: 0.001;
    position: absolute;
    z-index: 10;
    top: 0;
    left: 0;
    width: 40px;
    height: 40px;
    margin: -20px 0 0 -20px;
    background-color: currentColor;
    transform: translate3d(0,0,0);
  }

  .logo-animation .logo-letter svg {
    overflow: visible;
    fill: none;
    fill-rule: evenodd;
  }

  .logo-animation .line {
    fill: none;
    fill-rule: evenodd;
    stroke-linecap: square;
    stroke-width: 40;
    stroke: currentColor;
  }

  .logo-animation .fill {
    opacity: .001;
    stroke: currentColor;
    stroke-width: 40px;
  }

  .logo-text {
    opacity: .001;
    margin-top: .25em;
    font-weight: 400;
    font-size: 11px;
    line-height: 1;
    letter-spacing: .125em;
    text-align: justify;
    word-break: keep-all;
  }

  .logo-text:after {
    content: "";
    display: inline-block;
    width: 100%;
    height: 0;
    font-size: 0;
    line-height: 0;
  }
</style>

<div class="main-logo">
    <div class="logo-animation-wrapper">
      <div class="logo-animation">
        <div class="anime-logo">
          <div class="anime-logo-signs">
            <div class="logo-letter letter-a">
              <svg class="bounced" viewBox="0 0 200 240" width="200" height="200">
                <!-- <path class="line" d="M30 20h130c9.996 0 10 40 10 60v140H41c-11.004 0-11-40-11-60s-.004-60 10-60h110"/> -->
                <path class="line" d="M 6.9 53 L 7.5 35.3 L 0.8 35.3 A 1.568 1.568 0 0 1 0.511 35.276 Q 0 35.179 0 34.7 A 4.741 4.741 0 0 1 0.249 33.241 Q 0.649 32.005 1.692 30.561 A 15.521 15.521 0 0 1 1.7 30.55 A 8.133 8.133 0 0 1 2.652 29.441 Q 3.234 28.883 3.847 28.576 A 3.431 3.431 0 0 1 5.4 28.2 L 7.5 28.2 Q 7.316 21.017 7.132 17.565 A 104.183 104.183 0 0 0 7.1 17 Q 6.7 10.9 5.1 7.6 L 4.6 6.6 A 1.821 1.821 0 0 1 4.206 5.572 A 2.326 2.326 0 0 1 4.2 5.4 A 0.924 0.924 0 0 1 4.434 4.797 Q 4.68 4.502 5.185 4.254 A 4.308 4.308 0 0 1 5.3 4.2 Q 6.142 3.817 7.6 3.317 A 63.932 63.932 0 0 1 8.55 3 A 17.61 17.61 0 0 1 9.723 2.672 Q 12.231 2.049 17.7 1.15 A 85.968 85.968 0 0 1 26.453 0.19 A 107.91 107.91 0 0 1 32.95 0 A 87.709 87.709 0 0 1 35.673 0.039 Q 41.335 0.216 41.95 1.2 A 3.929 3.929 0 0 1 42.361 2.133 Q 42.652 3.081 42.693 4.478 A 16.07 16.07 0 0 1 42.7 4.95 A 14.175 14.175 0 0 1 42.679 5.751 Q 42.58 7.5 42 7.5 A 0.621 0.621 0 0 1 41.945 7.497 Q 41.788 7.481 41.3 7.4 A 9.894 9.894 0 0 0 40.266 7.207 Q 38.772 7 36.4 7 A 41.592 41.592 0 0 0 32.305 7.212 A 52.384 52.384 0 0 0 29.3 7.6 Q 26.168 8.095 24.259 8.589 A 20.793 20.793 0 0 0 23.5 8.8 L 21.6 9.5 Q 20.975 9.656 20.594 10.423 A 3.71 3.71 0 0 0 20.4 10.9 A 66.018 66.018 0 0 0 20.013 14.654 Q 19.6 20.006 19.6 28.2 L 35.8 28.2 Q 36.667 28.2 36.699 28.757 A 0.758 0.758 0 0 1 36.7 28.8 Q 36.7 30.6 35.101 32.999 A 6.554 6.554 0 0 0 35.1 33 Q 34.161 34.409 33.084 34.991 A 3.288 3.288 0 0 1 31.5 35.4 L 19.6 35.3 L 20.3 65.3 A 10.986 10.986 0 0 1 20.248 66.413 Q 20.109 67.774 19.6 68.5 Q 18.163 70.39 15.212 71.566 A 19.626 19.626 0 0 1 13.15 72.25 A 46.489 46.489 0 0 1 10.458 72.909 Q 7.663 73.5 5.6 73.5 Q 4.878 73.5 4.808 72.686 A 2.155 2.155 0 0 1 4.8 72.5 Q 4.8 72.175 4.842 71.934 A 1.641 1.641 0 0 1 4.9 71.7 A 3.796 3.796 0 0 0 5.336 70.525 Q 6.083 67.492 6.653 57.72 A 420.397 420.397 0 0 0 6.9 53 Z" vector-effect="non-scaling-stroke"/>
              </svg>
            </div>
            <div class="logo-letter letter-n">
              <svg class="bounced" viewBox="0 0 200 240" width="200" height="200">
                <path class="line" d="M170 220V60c0-31.046-8.656-40-19.333-40H49.333C38.656 20 30 28.954 30 60v160"/>
              </svg>
            </div>
            <div class="logo-letter letter-i">
              <svg class="bounced" viewBox="0 0 60 240" width="60" height="200">
                <path class="line" 
                        d="M30 20v200" 
                  data-d2="M30 100v120"
                />
              </svg>
            </div>
            <div class="logo-letter letter-m">
              <svg class="bounced" viewBox="0 0 340 240" width="340" height="200" fill="none" fill-rule="evenodd">
                <path class="line" 
                        d="M240,220 L240,60 C240,28.954305 231.344172,20 220.666667,20 C171.555556,20 254.832031,20 170,20 C85.1679688,20 168.444444,20 119.333333,20 C108.655828,20 100,28.954305 100,60 L100,220" 
                  data-d2="M310,220 L310,60 C310,28.954305 301.344172,20 290.666667,20 C241.555556,20 254.832031,110 170,110 C85.1679688,110 98.4444444,20 49.3333333,20 C38.6558282,20 30,28.954305 30,60 L30,220" 
                  data-d3="M310,220 L310,60 C310,28.954305 301.344172,20 290.666667,20 C241.555556,20 254.832031,20 170,20 C85.1679688,20 98.4444444,20 49.3333333,20 C38.6558282,20 30,28.954305 30,60 L30,220" 
                />
              </svg>
            </div>
            <div class="logo-letter letter-e">
              <svg class="bounced" viewBox="0 0 200 240" width="200" height="200">
                <path class="line" d="M50 140h110c10 0 10-40 10-60s0-60-10-60H40c-10 0-10 40-10 60v80c0 20 0 60 10 60h130"/>
              </svg>
            </div>
            <div class="bounce">
              <svg viewBox="0 0 1000 260" width="1000" height="260" fill="none">
                <path d="M630,240 C630,111.154418 608.971354,40 530.160048,40 C451.348741,40 430,127.460266 430,210"/>
              </svg>
              <div class="dot"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>