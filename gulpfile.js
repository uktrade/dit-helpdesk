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
    folder: './assets/',
    source: './assets/global.scss',
    destination: './dit_helpdesk/static/css/'
  },
  javascripts: {
    source: './assets/**/*.js',
    destination: './dit_helpdesk/static/js/'
  },
  govukFrontendAssets: {
    source: './node_modules/govuk-frontend/assets/**/*.*',
    destination: './dit_helpdesk/static/'
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

const watch = () => {
  gulp.watch(paths.styles.folder, styles)
}

gulp.task('default', watch)
gulp.task('styles', styles)
gulp.task('javascripts', javascripts)
gulp.task('copy', copyAssets)
