# Custom ggplot theme for Moral Psychology Research Lab, Harvard University
# Created by Xavier Roberts-Gaal, January 2023

theme_mprl <- function() {
  
  font <- "Arial"
  
  theme_bw() %+replace%
    theme(
      
      # grid elements
      
      panel.grid.major = element_blank(),
      
      panel.grid.minor = element_blank(),
      
      legend.key = element_blank(),
      
      # text elements
      
      plot.title = element_text(size = 12,
                                family = font,
                                face = 'bold',
                                margin = margin(0,0,10,0)
      ),
      
      axis.title = element_text(size = 12,
                                family = font,
                                face = 'bold'),
      
      axis.text = element_text(size = 10,
                               family = font,
                               face = 'bold'),
      
      legend.title = element_text(family = font,
                                  face = 'bold',
                                  margin = margin(b=10)),
      
      legend.text = element_text(size = 10, face = "bold"),
      
      strip.text.x = element_text(face = 'bold'),
      
      strip.text.y = element_text(face = 'bold'),
      
      # point elements
    )
}
