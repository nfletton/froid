# Require any additional compass plugins here.
require 'compass'
require 'singularitygs'
require 'breakpoint'

# Change this to :production when ready to deploy the CSS to the live server.
#environment = :development
environment = :production

# Set this to the root of your project when deployed:
http_path = "/assets"
css_dir = "css"
sass_dir = "sass"
images_dir = "img"
javascripts_dir = "js"

output_style = (environment == :development) ? :expanded : :compressed

# To enable relative paths to assets via compass helper functions. Uncomment:
# relative_assets = true

# To disable debugging comments that display the original location of your selectors. Uncomment:
# line_comments = false


# If you prefer the indented syntax, you might want to regenerate this
# project again passing --syntax sass, or you can uncomment this:
# preferred_syntax = :sass
# and then run:
# sass-convert -R --from scss --to sass sass scss && rm -rf sass && mv scss sass
