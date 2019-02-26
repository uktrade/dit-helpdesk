'use strict'

const gulp = require('gulp')
const sass = require('gulp-sass')
// const rev = require('gulp-rev')
const sourcemaps = require('gulp-sourcemaps')
const cssnano = require('gulp-cssnano')

sass.compiler = require('node-sass')

// const environment = process.env.NODE_ENV || 'dev'

const paths = {
  styles: {
    folder: './dit_helpdesk/static/',
    source: './dit_helpdesk/static/global.scss',
    destination: './dit_helpdesk/static_collected/css/'
  },
  javascripts: {
    source: './assets/**/*.js',
    accessibleAutocomplete: './node_modules/accessible-autocomplete/dist/accessible-autocomplete.min.js*',
    destination: './dit_helpdesk/static_collected/js/'
  },
  govukFrontendAssets: {
    source: './node_modules/govuk-frontend/assets/**/*.*',
    destination: './dit_helpdesk/static_collected/'
  },
  manifest: './manifest'
}

const styles = () => {
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

const javascripts = () => {
  return gulp.src(paths.javascripts.source)
    .pipe(gulp.dest(paths.javascripts.destination))
}

const copyAssets = () => {
  return gulp.src(paths.govukFrontendAssets.source)
    .pipe(gulp.dest(paths.govukFrontendAssets.destination))
}

const copyAccessibleAutocomplete = () => {
  return gulp.src(paths.javascripts.accessibleAutocomplete)
    .pipe(gulp.dest(paths.javascripts.destination))
}

const watch = () => {
  gulp.watch(paths.styles.folder, styles)
}

gulp.task('default', watch)
gulp.task('styles', styles)
gulp.task('javascripts', javascripts)
gulp.task('copy', gulp.parallel(copyAssets, copyAccessibleAutocomplete))
gulp.task('build:all', gulp.parallel(copyAssets, copyAccessibleAutocomplete, styles, javascripts))
