"""
Unified optimizer implementing Active Inference and Genetic Algorithms
across all trading domains (portfolio, risk, and execution).
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from decimal import Decimal
import logging
from datetime import datetime
from ..core.system_state import SystemState, Position, PortfolioState, RiskMetrics, ExecutionState, PerformanceMetrics

@dataclass
class OptimizedParameters:
    """Parameters optimized across all domains"""
    # Portfolio parameters
    position_sizes: Dict[str, Decimal]
    target_allocations: Dict[str, float]
    rebalance_thresholds: Dict[str, float]
    
    # Risk parameters
    position_var_limits: Dict[str, float]
    stop_loss_levels: Dict[str, Decimal]
    take_profit_levels: Dict[str, Decimal]
    heat_capacity: float
    
    # Execution parameters
    order_types: Dict[str, str]
    execution_styles: Dict[str, str]
    timing_parameters: Dict[str, float]

@dataclass
class SystemBelief:
    """System's beliefs about optimal parameters"""
    # Beliefs about optimal parameter values
    portfolio_beliefs: Dict[str, float]
    risk_beliefs: Dict[str, float]
    execution_beliefs: Dict[str, float]
    
    # Uncertainty in beliefs
    portfolio_uncertainty: Dict[str, float]
    risk_uncertainty: Dict[str, float]
    execution_uncertainty: Dict[str, float]
    
    # Overall system confidence
    confidence: float

class UnifiedOptimizer:
    """
    Implements Active Inference and Genetic Algorithms to optimize
    all aspects of trading system performance.
    """
    
    def __init__(self, config: Dict[str, Any], market_analyzer: Any):
        """
        Initialize the unified optimizer.
        
        Args:
            config: Configuration parameters
            market_analyzer: Interface to market analysis system
        """
        self.config = config
        self.market_analyzer = market_analyzer
        self.logger = logging.getLogger(__name__)
        self.system_belief = self._initialize_beliefs()
        self.population: List[OptimizedParameters] = []
        self.last_state: Optional[SystemState] = None
        
        # Optimization parameters
        self.learning_rate = config.get("learning_rate", 0.01)
        self.population_size = config.get("population_size", 100)
        self.num_generations = config.get("num_generations", 10)
        self.mutation_rate = config.get("mutation_rate", 0.1)
        self.exploration_factor = config.get("exploration_factor", 0.1)
        
    def _initialize_beliefs(self) -> SystemBelief:
        """Initialize system beliefs with reasonable defaults"""
        return SystemBelief(
            portfolio_beliefs={
                'position_size': 0.1,  # 10% of portfolio per position
                'max_concentration': 0.3,  # 30% max in single asset
                'cash_buffer': 0.1  # 10% cash buffer
            },
            risk_beliefs={
                'var_limit': 0.02,  # 2% VaR limit
                'stop_loss': 0.02,  # 2% stop loss
                'heat_capacity': 0.8  # 80% max risk capacity
            },
            execution_beliefs={
                'market_impact_threshold': 0.001,  # 0.1% market impact limit
                'spread_threshold': 0.0005,  # 0.05% max spread
                'timing_sensitivity': 0.5  # Medium timing sensitivity
            },
            portfolio_uncertainty={'position_size': 0.2, 'max_concentration': 0.2, 'cash_buffer': 0.2},
            risk_uncertainty={'var_limit': 0.2, 'stop_loss': 0.2, 'heat_capacity': 0.2},
            execution_uncertainty={'market_impact_threshold': 0.2, 'spread_threshold': 0.2, 'timing_sensitivity': 0.2},
            confidence=0.5
        )
    
    def update_beliefs(self, system_state: SystemState) -> None:
        """
        Update beliefs about optimal parameters using Active Inference.
        
        Args:
            system_state: Current state of the entire system
        """
        try:
            # Get market analysis
            market_analysis = self.market_analyzer.get_current_analysis()
            
            # Calculate prediction errors across all domains
            portfolio_errors = self._calculate_portfolio_errors(system_state)
            risk_errors = self._calculate_risk_errors(system_state)
            execution_errors = self._calculate_execution_errors(system_state)
            
            # Update beliefs using precision-weighted errors
            self._update_portfolio_beliefs(portfolio_errors)
            self._update_risk_beliefs(risk_errors)
            self._update_execution_beliefs(execution_errors)
            
            # Update overall confidence based on prediction accuracy
            self.system_belief.confidence = self._calculate_confidence(
                portfolio_errors, risk_errors, execution_errors)
            
        except Exception as e:
            self.logger.error(f"Error updating beliefs: {str(e)}")
    
    def generate_optimized_parameters(self, system_state: SystemState) -> OptimizedParameters:
        """
        Generate optimized parameters using genetic algorithms.
        
        Args:
            system_state: Current state of the entire system
            
        Returns:
            Optimized parameters across all domains
        """
        try:
            # Initialize population
            self.population = self._initialize_population()
            self.last_state = system_state
            
            # Evolve population
            for generation in range(self.num_generations):
                # Evaluate fitness
                fitness_scores = [
                    self._evaluate_fitness(params, system_state)
                    for params in self.population
                ]
                
                # Select parents
                parents = self._select_parents(fitness_scores)
                
                # Create new population
                self.population = self._create_new_population(parents)
                
                # Apply mutation
                self._apply_mutation()
            
            # Return best parameters
            return self._select_best_parameters()
            
        except Exception as e:
            self.logger.error(f"Error generating parameters: {str(e)}")
            return self._get_default_parameters()
    
    def _calculate_portfolio_errors(self, state: SystemState) -> Dict[str, float]:
        """Calculate prediction errors for portfolio parameters"""
        return {
            'position_size': self._calculate_position_size_error(state),
            'concentration': self._calculate_concentration_error(state),
            'cash_buffer': self._calculate_cash_buffer_error(state)
        }
    
    def _calculate_risk_errors(self, state: SystemState) -> Dict[str, float]:
        """Calculate prediction errors for risk parameters"""
        return {
            'var': self._calculate_var_error(state),
            'stop_loss': self._calculate_stop_loss_error(state),
            'heat': self._calculate_heat_error(state)
        }
    
    def _calculate_execution_errors(self, state: SystemState) -> Dict[str, float]:
        """Calculate prediction errors for execution parameters"""
        return {
            'market_impact': self._calculate_market_impact_error(state),
            'spread': self._calculate_spread_error(state),
            'timing': self._calculate_timing_error(state)
        }
    
    def _evaluate_fitness(self, params: OptimizedParameters, state: SystemState) -> float:
        """
        Evaluate fitness of parameters based on risk-adjusted returns.
        
        Args:
            params: Parameters to evaluate
            state: Current system state
            
        Returns:
            Fitness score based on risk-adjusted performance
        """
        try:
            # Simulate parameter application
            simulated_state = self._simulate_parameters(params, state)
            
            # Calculate primary fitness components
            risk_adjusted_return = simulated_state.calculate_risk_adjusted_returns()
            sharpe_ratio = simulated_state.performance_metrics.sharpe_ratio
            recovery_factor = simulated_state.performance_metrics.recovery_factor
            
            # Calculate penalty components
            concentration_penalty = self._calculate_concentration_penalty(simulated_state)
            risk_penalty = self._calculate_risk_penalty(simulated_state)
            execution_penalty = self._calculate_execution_penalty(simulated_state)
            
            # Combine components with weights
            fitness = (
                0.4 * risk_adjusted_return +
                0.3 * sharpe_ratio +
                0.2 * recovery_factor - 
                0.1 * (concentration_penalty + risk_penalty + execution_penalty)
            )
            
            return max(fitness, 0.0)  # Ensure non-negative fitness
            
        except Exception as e:
            self.logger.error(f"Error evaluating fitness: {str(e)}")
            return 0.0
    
    def _simulate_parameters(self, params: OptimizedParameters, 
                           current_state: SystemState) -> SystemState:
        """
        Simulate application of parameters to current state.
        
        Args:
            params: Parameters to simulate
            current_state: Current system state
            
        Returns:
            Simulated future state
        """
        try:
            # Create a copy of current portfolio state
            portfolio = current_state.portfolio_state
            
            # Calculate position adjustments
            position_adjustments = {}
            for symbol, target_size in params.position_sizes.items():
                current_size = Decimal('0')
                if symbol in portfolio.positions:
                    current_size = portfolio.positions[symbol].size
                position_adjustments[symbol] = target_size - current_size
            
            # Simulate transaction costs
            transaction_costs = sum(
                abs(float(adj)) * 0.001  # Assume 0.1% transaction cost
                for adj in position_adjustments.values()
            )
            
            # Create simulated portfolio state
            simulated_positions = {}
            for symbol, target_size in params.position_sizes.items():
                current_pos = portfolio.positions.get(symbol)
                if current_pos:
                    simulated_positions[symbol] = Position(
                        symbol=symbol,
                        size=target_size,
                        entry_price=current_pos.entry_price,
                        current_price=current_pos.current_price,
                        unrealized_pnl=current_pos.unrealized_pnl,
                        realized_pnl=current_pos.realized_pnl,
                        entry_time=current_pos.entry_time,
                        stop_loss=params.stop_loss_levels.get(symbol),
                        take_profit=params.take_profit_levels.get(symbol)
                    )
                else:
                    # Simulate new position
                    market_data = self.market_analyzer.get_current_price(symbol)
                    simulated_positions[symbol] = Position(
                        symbol=symbol,
                        size=target_size,
                        entry_price=Decimal(str(market_data['price'])),
                        current_price=Decimal(str(market_data['price'])),
                        unrealized_pnl=Decimal('0'),
                        realized_pnl=Decimal('0'),
                        entry_time=datetime.now(),
                        stop_loss=params.stop_loss_levels.get(symbol),
                        take_profit=params.take_profit_levels.get(symbol)
                    )
            
            simulated_portfolio = PortfolioState(
                positions=simulated_positions,
                cash_balance=portfolio.cash_balance - Decimal(str(transaction_costs)),
                total_value=portfolio.total_value - Decimal(str(transaction_costs)),
                asset_allocation=self._calculate_allocation(simulated_positions),
                margin_used=portfolio.margin_used,
                margin_available=portfolio.margin_available
            )
            
            # Create simulated system state
            return SystemState(
                timestamp=datetime.now(),
                portfolio_state=simulated_portfolio,
                risk_metrics=self._simulate_risk_metrics(simulated_portfolio, params),
                execution_state=self._simulate_execution_state(params),
                market_state=current_state.market_state,
                performance_metrics=self._simulate_performance_metrics(
                    simulated_portfolio, transaction_costs)
            )
            
        except Exception as e:
            self.logger.error(f"Error simulating parameters: {str(e)}")
            return current_state
    
    def _crossover(self, parent1: OptimizedParameters, 
                  parent2: OptimizedParameters) -> Tuple[OptimizedParameters, OptimizedParameters]:
        """
        Perform crossover between two parents to create two children.
        Uses uniform crossover with random gene selection.
        """
        try:
            child1_params = {}
            child2_params = {}
            
            # Crossover position sizes
            child1_sizes = {}
            child2_sizes = {}
            for symbol in set(parent1.position_sizes.keys()) | set(parent2.position_sizes.keys()):
                if np.random.random() < 0.5:
                    child1_sizes[symbol] = parent1.position_sizes.get(symbol, Decimal('0'))
                    child2_sizes[symbol] = parent2.position_sizes.get(symbol, Decimal('0'))
                else:
                    child1_sizes[symbol] = parent2.position_sizes.get(symbol, Decimal('0'))
                    child2_sizes[symbol] = parent1.position_sizes.get(symbol, Decimal('0'))
            
            # Crossover risk parameters
            child1_stop_loss = {}
            child2_stop_loss = {}
            child1_take_profit = {}
            child2_take_profit = {}
            for symbol in set(parent1.stop_loss_levels.keys()) | set(parent2.stop_loss_levels.keys()):
                if np.random.random() < 0.5:
                    child1_stop_loss[symbol] = parent1.stop_loss_levels.get(symbol)
                    child2_stop_loss[symbol] = parent2.stop_loss_levels.get(symbol)
                    child1_take_profit[symbol] = parent1.take_profit_levels.get(symbol)
                    child2_take_profit[symbol] = parent2.take_profit_levels.get(symbol)
                else:
                    child1_stop_loss[symbol] = parent2.stop_loss_levels.get(symbol)
                    child2_stop_loss[symbol] = parent1.stop_loss_levels.get(symbol)
                    child1_take_profit[symbol] = parent2.take_profit_levels.get(symbol)
                    child2_take_profit[symbol] = parent1.take_profit_levels.get(symbol)
            
            # Create children
            child1 = OptimizedParameters(
                position_sizes=child1_sizes,
                target_allocations=parent1.target_allocations,  # Keep parent's allocation
                rebalance_thresholds=parent1.rebalance_thresholds,
                position_var_limits=parent1.position_var_limits,
                stop_loss_levels=child1_stop_loss,
                take_profit_levels=child1_take_profit,
                heat_capacity=parent1.heat_capacity if np.random.random() < 0.5 else parent2.heat_capacity,
                order_types=parent1.order_types,
                execution_styles=parent1.execution_styles,
                timing_parameters=parent1.timing_parameters
            )
            
            child2 = OptimizedParameters(
                position_sizes=child2_sizes,
                target_allocations=parent2.target_allocations,
                rebalance_thresholds=parent2.rebalance_thresholds,
                position_var_limits=parent2.position_var_limits,
                stop_loss_levels=child2_stop_loss,
                take_profit_levels=child2_take_profit,
                heat_capacity=parent2.heat_capacity if np.random.random() < 0.5 else parent1.heat_capacity,
                order_types=parent2.order_types,
                execution_styles=parent2.execution_styles,
                timing_parameters=parent2.timing_parameters
            )
            
            return child1, child2
            
        except Exception as e:
            self.logger.error(f"Error in crossover: {str(e)}")
            return parent1, parent2
    
    def _mutate_parameters(self, params: OptimizedParameters) -> None:
        """
        Apply mutation to parameters while maintaining validity constraints.
        """
        try:
            # Mutate position sizes
            for symbol in params.position_sizes:
                if np.random.random() < self.mutation_rate:
                    current_size = params.position_sizes[symbol]
                    mutation_factor = 1 + (np.random.random() - 0.5) * 0.2  # ±10% change
                    params.position_sizes[symbol] = current_size * Decimal(str(mutation_factor))
            
            # Mutate stop loss and take profit levels
            for symbol in params.stop_loss_levels:
                if np.random.random() < self.mutation_rate:
                    current_stop = params.stop_loss_levels[symbol]
                    if current_stop:
                        mutation_factor = 1 + (np.random.random() - 0.5) * 0.1  # ±5% change
                        params.stop_loss_levels[symbol] = current_stop * Decimal(str(mutation_factor))
                
                if np.random.random() < self.mutation_rate:
                    current_tp = params.take_profit_levels[symbol]
                    if current_tp:
                        mutation_factor = 1 + (np.random.random() - 0.5) * 0.1
                        params.take_profit_levels[symbol] = current_tp * Decimal(str(mutation_factor))
            
            # Mutate heat capacity
            if np.random.random() < self.mutation_rate:
                mutation_factor = 1 + (np.random.random() - 0.5) * 0.2
                params.heat_capacity = max(0.1, min(1.0, params.heat_capacity * mutation_factor))
            
            # Mutate execution parameters
            for symbol in params.execution_styles:
                if np.random.random() < self.mutation_rate:
                    # Randomly switch between execution styles
                    styles = ['MKT', 'LMT', 'TWAP', 'VWAP']
                    params.execution_styles[symbol] = np.random.choice(styles)
            
        except Exception as e:
            self.logger.error(f"Error in mutation: {str(e)}")
    
    def _select_best_parameters(self) -> OptimizedParameters:
        """
        Select best parameters from population based on fitness.
        """
        try:
            if not self.last_state:
                return self._get_default_parameters()
            
            # Calculate fitness for all parameters
            fitness_scores = [
                self._evaluate_fitness(params, self.last_state)
                for params in self.population
            ]
            
            # Select best parameters
            best_idx = np.argmax(fitness_scores)
            return self.population[best_idx]
            
        except Exception as e:
            self.logger.error(f"Error selecting best parameters: {str(e)}")
            return self._get_default_parameters()
    
    def _calculate_allocation(self, positions: Dict[str, Position]) -> Dict[str, float]:
        """Calculate portfolio allocation percentages"""
        total_value = sum(pos.size * pos.current_price for pos in positions.values())
        if total_value == 0:
            return {}
        return {
            symbol: float(pos.size * pos.current_price / total_value)
            for symbol, pos in positions.items()
        }
    
    def _simulate_risk_metrics(self, portfolio: PortfolioState, 
                             params: OptimizedParameters) -> RiskMetrics:
        """Simulate risk metrics for proposed parameters"""
        position_values = {
            symbol: pos.size * pos.current_price
            for symbol, pos in portfolio.positions.items()
        }
        total_value = sum(position_values.values())
        
        position_var = {
            symbol: float(value / total_value) * params.position_var_limits.get(symbol, 0.02)
            for symbol, value in position_values.items()
        }
        
        return RiskMetrics(
            portfolio_var=sum(position_var.values()),
            portfolio_volatility=0.02,  # Placeholder
            position_var=position_var,
            position_volatility={s: 0.02 for s in position_var},  # Placeholder
            correlation_matrix={},  # Would calculate actual correlations
            max_drawdown=0.0,
            sharpe_ratio=0.0,
            sortino_ratio=0.0,
            current_heat=sum(position_var.values())
        )
    
    def _simulate_execution_state(self, params: OptimizedParameters) -> ExecutionState:
        """Simulate execution state for proposed parameters"""
        return ExecutionState(
            pending_orders=[],
            recent_fills=[],
            execution_latency=0.0,
            spread_costs={},
            market_impact={},
            order_book_state={}
        )
    
    def _simulate_performance_metrics(self, portfolio: PortfolioState,
                                   transaction_costs: float) -> PerformanceMetrics:
        """Simulate performance metrics for proposed parameters"""
        return PerformanceMetrics(
            total_return=0.0,
            risk_adjusted_return=0.0,
            win_rate=0.0,
            profit_factor=0.0,
            avg_win_loss_ratio=0.0,
            max_drawdown=0.0,
            recovery_factor=0.0,
            sharpe_ratio=0.0,
            sortino_ratio=0.0,
            calmar_ratio=0.0,
            portfolio_turnover=0.0,
            transaction_costs=transaction_costs
        )
