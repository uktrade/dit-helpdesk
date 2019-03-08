'use strict'

const gulp = require('gulp')
const sass = require('gulp-sass')
// const rev = require('gulp-rev')
const sourcemaps = require('gulp-sourcemaps')
const cssnano = require('gulp-cssnano')
const taskListing = require('gulp-task-listing')

sass.compiler = require('node-sass')

// const environment = process.env.NODE_ENV || 'dev'

const paths = {
  styles: {
    watch: './assets/scss/**/*.scss',
    source: './assets/scss/global.scss',
    destination: './dit_helpdesk/static_collected/css/'
  },
  javascripts: {
    watch: './assets/javascript/**/*.js',
    source: './assets/javascript/**/*.js',
    accessibleAutocomplete: './node_modules/accessible-autocomplete/dist/accessible-autocomplete.min.js*',
    destination: './dit_helpdesk/static_collected/js/'
  },
  govukFrontendAssets: {
    source: './node_modules/govuk-frontend/assets/**/*.*',
    destination: './dit_helpdesk/static_collected/'
  },
  manifest: './manifest'
}

const buildStyles = () => {
  return gulp.src(paths.styles.source)
    .pipe(sass({
      includePaths: 'node_modules'
    }))
    .pipe(sourcemaps.init())
    // .pipe(rev())
    .pipe(sass().on('error', sass.logError))
    .pipe(cssnano())
    .pipe(sourcemaps.write('./'))
    .pipe(gulp.dest(paths.styles.destination))
    // .pipe(rev.manifest({ merge: true }))
    // .pipe(gulp.dest(paths.manifest))
}

const buildJavascripts = () => {
  return gulp.src(paths.javascripts.source, { sourcemaps: true })
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
  return gulp.watch(paths.javascripts.watch, buildStyles)
}

const copy = gulp.parallel(copyGOVUKFrontendAssets, copyAccessibleAutocomplete)
const watch = gulp.parallel(watchStyles, watchJavascripts)
const build = gulp.parallel(buildStyles, buildJavascripts)

gulp.task('default', taskListing)
gulp.task('copyExternalAssets', copy)
gulp.task('watch', gulp.series(copy, watch))
gulp.task('build', gulp.series(copy, build))

gulp.task('watch:styles', watchStyles)
gulp.task('watch:javascripts', watchJavascripts)
gulp.task('build:styles', buildStyles)
gulp.task('build:javascripts', buildJavascripts)
