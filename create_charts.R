# R code to reproduce charts from "Computational principles underpinning the 
# evolution of cultural learning mechanisms" by Xavier Roberts-Gaal and
# Fiery Cushman, Department of Psychology, Harvard University, 10 May 2023

##### Housekeeping #####

if (!require("pacman")) { install.packages("pacman"); require("pacman") }
pacman::p_load(tidyverse, scales, svglite, rstudioapi)

setwd(dirname(getActiveDocumentContext()$path))
source("theme_mprl_ggplot.R") # Lab ggplot theme

theme_set(theme_mprl())
CHART_TO_EPS <- TRUE # Set to FALSE to output .png chart graphics

##### Figure 1: Analysis of Model 1 #####

df_fig1_freq <- read_csv("data/model1_simulations_aggregated_frequencies.csv") 

df_fig1_pay <- read_csv("data/model1_simulations_aggregated_payoffs.csv")

df_fig1 <- df_fig1_freq %>% 
  left_join(df_fig1_pay, by = c("strategy", "kappa", "delta", "sim")) %>%
  pivot_wider(names_from = strategy,
              values_from = c(avg_payoff, count)) %>%
  filter(kappa == 0.4) %>%
  arrange(delta) %>%
  mutate(
    prop_MF = count_MF / 120,
    payoff_diff = avg_payoff_MF - avg_payoff_IL,
    across(where(is.numeric), ~ round(., 2)))

(fig1 <- ggplot(df_fig1, aes(x = prop_MF, y = payoff_diff, color = delta)) +
  scale_color_viridis_c(option="C", name = "Shock\nprobability") +
  geom_point() +
  ylim(-1,1) +
  xlim(0,1) +
  geom_path() +
  geom_hline(yintercept=0) +
  geom_vline(xintercept=0.5) +
  xlab("Proportion of social learners") +
  ylab("Social learner relative payoff") +
  theme(legend.position = "right",
        legend.box.background = element_rect(fill = "transparent", color = NA),
        legend.key.height = unit(1.5, "cm")))

##### Figure 2: Analysis of Model 2 #####

df_fig2 <- read_csv("data/model2_simulations_aggregated.csv") %>%
  mutate(Lambda = lambda,
         prop = count/120,
         across(where(is.numeric), ~ round(., 2))) %>%
  filter(kappa == 0.4, 
         lambda %in% c(0.1, 0.2, 0.3))

(fig2 <- ggplot(data = df_fig2, 
                aes(x = delta, y = prop, color = strategy)) +
    scale_color_manual(values = c("IL" = "green", "MB" = "blue", "MF" = "orange")) +
    scale_alpha(guide='none') +
    scale_x_continuous(n.breaks = 5, labels = label_number(accuracy = 0.01), 
                       name = "Shock probability") +
    scale_y_continuous(n.breaks = 5, labels = label_number(accuracy = 0.01), 
                       limits = c(0, 1), name = "Concentration of type") +
    geom_jitter(width = 0.01, height = 0.01, shape = 1) +
    geom_smooth(aes(x = delta, y = prop), formula = y ~ x, method = "lm", se=F) +
    facet_wrap( ~ Lambda, nrow = 3, labeller = label_both))

##### Figure 3: Comparison of Models 1 and 2 #####

# Implements the equilibrium proportion of SL from Giuliano and Nunn (2021)
prop_SL <- function(delta, kappa=0.4) {
  if (delta >= kappa) { return(0) }
  else { return((-delta + kappa) / (kappa * (1 - delta)))}
}

# Constructs dataframe for plotting
deltas <- c(0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)
model1 <- data.frame(
  Delta = deltas,
  SL = map_dbl(deltas, prop_SL),
  Model = 1
)

model2 <- df_fig2 %>%
  filter(lambda == 0.3) %>%
  select(-count) %>%
  pivot_wider(names_from = strategy,
              values_from = prop) %>%
  mutate(SL = MB + MF,
         Model = 2,
         Delta = delta) %>%
  select(Delta, SL, Model)

df_fig3 <- rbind(model1, model2)
df_fig3$Model <- factor(df_fig3$Model, levels = c("1", "2"))

# Creates chart
(fig3 <- ggplot(data = df_fig3, aes(x = Delta, y = SL, color = Model)) +
  geom_line(linewidth = 1.5) +
  scale_color_manual(labels = c("1: SL", "2: MF+MB"), values = c("#0D0887FF", "#ED7953FF")) +
  xlab("Shock probability") +
  ylab("Social learner concentration"))

##### Save images from plots #####

if (CHART_TO_EPS) {
  print("Saving .eps files")
  ggsave(filename = "plots/fig_model1.eps", 
         plot = fig1,
         device = "eps",
         width = 6.25,
         height = 4)
  ggsave(filename = "plots/fig_model2.eps",
         plot = fig2,
         device = "eps",
         width = 6.25,
         height = 10.4)
  ggsave(filename = "plots/fig_modelcomparison.eps",
         plot = fig3,
         device = "eps",
         width = 6.25,
         height = 4)
} else {
  print("Saving .png files")
  ggsave(filename = "plots/fig1.png",
         plot = fig1,
         device = "png",
         width = 6.25,
         height = 4)
  ggsave(filename = "plots/fig2.png",
         plot = fig2,
         device = "png",
         width = 6.25,
         height = 10.4)
  ggsave(filename = "plots/fig3.png",
         plot = fig3,
         device = "png",
         width = 6.25,
         height = 4)
}
