'use strict'

const gulp = require('gulp')

const autoprefixer = require('autoprefixer')
const cssnano = require('gulp-cssnano')
const oldie = require('oldie')({
  rgba: { filter: true },
  rem: { disable: true },
  unmq: { disable: true },
  pseudo: { disable: true }
  // more rules go here
})
const postcss = require('gulp-postcss')
const rename = require('gulp-rename')
const sass = require('gulp-sass')
const sourcemaps = require('gulp-sourcemaps')
const taskListing = require('gulp-task-listing')

const browserify = require('browserify')
const source = require('vinyl-source-stream')
const buffer = require('vinyl-buffer')
const uglify = require('gulp-uglify')
const log = require('gulplog')

sass.compiler = require('node-sass')

// const environment = process.env.NODE_ENV || 'dev'

const paths = {
  styles: {
    watch: './assets/scss/**/*.scss',
    source: './assets/scss/global.scss',
    oldie: './assets/scss/oldie.scss',
    destination: './dit_helpdesk/static_collected/css/'
  },
  javascripts: {
    watch: './assets/javascript/**/*.js',
    source: './assets/javascript/**/*.js',
    accessibleAutocomplete: './node_modules/govuk-country-and-territory-autocomplete/dist/*.(js|js.map)',
    destination: './dit_helpdesk/static_collected/js/'
  },
  govukFrontendAssets: {
    source: './node_modules/govuk-frontend/assets/**/*.*',
    destination: './dit_helpdesk/static_collected/'
  },
  manifest: './manifest'
}

const buildStylesForModernBrowsers = () => {
  return gulp.src(paths.styles.source)
    .pipe(sourcemaps.init())
    .pipe(sass({
      includePaths: 'node_modules'
    }).on('error', sass.logError))
    .pipe(
      postcss([
        autoprefixer
      ])
    )
    .pipe(cssnano())
    .pipe(rename({
      extname: '.min.css'
    }))
    .pipe(sourcemaps.write('./'))
    .pipe(gulp.dest(paths.styles.destination))
}

const buildStylesForOldIE = () => {
  return gulp.src(paths.styles.oldie)
    .pipe(sass({
      includePaths: 'node_modules'
    }).on('error', sass.logError))
    .pipe(
      postcss([
        autoprefixer,
        oldie
      ])
    )
    .pipe(cssnano())
    .pipe(rename({
      basename: 'global-oldie',
      extname: '.min.css'
    }))
    .pipe(sourcemaps.write('./'))
    .pipe(gulp.dest(paths.styles.destination))
}

const buildJavascripts = () => {
  return gulp.src([
      paths.javascripts.source,
      '!assets/javascript/global.js',
      '!assets/javascript/modules/**',
      '!assets/javascript/vendor/**/*'
    ], { sourcemaps: true })
    .pipe(gulp.dest(paths.javascripts.destination))
}

const compileGovukFrontend = () => {
  var b = browserify({
    entries: [
      './assets/javascript/global.js'
    ],
    debug: true,
    standalone: 'DITGlobals'
  });

  return b.bundle()
    .pipe(source('global.js'))
    .pipe(buffer())
    .pipe(sourcemaps.init({loadMaps: true}))
    // Add transformation tasks to the pipeline here.
    .pipe(uglify({ie8:true}))
    .on('error', log.error)
    .pipe(sourcemaps.write('./'))
    // .pipe(rename({
    //   extname: '.min.js'
    // }))
    .pipe(gulp.dest(paths.javascripts.destination))
}

const copyGOVUKFrontendAssets = () => {
  return gulp.src(paths.govukFrontendAssets.source)
    .pipe(gulp.dest(paths.govukFrontendAssets.destination))
}

const copyAccessibleAutocomplete = () => {
  return gulp.src(paths.javascripts.accessibleAutocomplete)
    .pipe(gulp.dest(paths.javascripts.destination))
}

const watchStyles = () => {
  return gulp.watch(paths.styles.watch, buildStyles)
}

const watchJavascripts = () => {
  return gulp.watch(paths.javascripts.watch, buildJavascripts)
}

const buildStyles = gulp.parallel(buildStylesForModernBrowsers, buildStylesForOldIE)

const copy = gulp.parallel(copyGOVUKFrontendAssets, copyAccessibleAutocomplete)
const watch = gulp.parallel(watchStyles, watchJavascripts, compileGovukFrontend)
const build = gulp.parallel(buildStyles, buildJavascripts, compileGovukFrontend)

gulp.task('default', taskListing)
gulp.task('copyExternalAssets', copy)
gulp.task('watch', gulp.series(copy, watch))
gulp.task('build', gulp.series(copy, build))

gulp.task('watch:styles', watchStyles)
gulp.task('watch:javascripts', watchJavascripts)
gulp.task('build:styles', buildStyles)
gulp.task('build:javascripts', buildJavascripts)
